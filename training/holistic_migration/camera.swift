// Built-in-only BGRA pipe. --self-test never enumerates or opens hardware.
import Foundation
import AVFoundation
import CoreMedia
import CoreVideo
import CryptoKit
import Darwin

enum CameraError: Error { case invalid(String) }
let builtinType = AVCaptureDevice.DeviceType.builtInWideAngleCamera.rawValue
struct Descriptor {
    let type: String
    let continuity: Bool
    let identity: String
}
func selectDevice(_ devices: [Descriptor]) throws -> Int {
    let eligible = devices.indices.filter {
        devices[$0].type == builtinType && !devices[$0].continuity && !devices[$0].identity.isEmpty
    }
    guard eligible.count == 1 else { throw CameraError.invalid("ambiguous-or-missing-built-in") }
    return eligible[0]
}
func packedRows(_ source: UnsafeRawBufferPointer, width: Int, height: Int, stride: Int) throws -> Data {
    guard width > 0, width <= 4096, height > 0, height <= 2160,
          stride >= width * 4, source.count >= stride * height else {
        throw CameraError.invalid("invalid-buffer-layout")
    }
    var data = Data(capacity: width * height * 4)
    let bytes = source.bindMemory(to: UInt8.self)
    for row in 0..<height {
        let start = row * stride
        data.append(contentsOf: bytes[start..<(start + width * 4)])
    }
    return data
}
struct WireEncoder {
    var dimensions: [Int]? = nil
    var last: Double? = nil
    mutating func packet(_ payload: Data, width: Int, height: Int, seconds: Double) throws -> Data {
        guard width > 0, width <= 4096, height > 0, height <= 2160,
              payload.count == width * height * 4 else { throw CameraError.invalid("invalid-payload") }
        let current = [width, height]
        guard dimensions == nil || dimensions == current else { throw CameraError.invalid("reconfiguration") }
        let timestamp = floor(seconds * 1000)
        guard seconds.isFinite, timestamp.isFinite, timestamp >= 0, timestamp <= 9007199254740992,
              last == nil || timestamp > last! else { throw CameraError.invalid("invalid-timestamp") }
        var bits = timestamp.bitPattern.bigEndian
        var size = UInt32(payload.count).bigEndian
        var result = Data(bytes: &bits, count: 8)
        result.append(Data(bytes: &size, count: 4))
        result.append(payload)
        dimensions = current; last = timestamp
        return result
    }
}
func require(_ condition: @autoclosure () -> Bool, _ name: String) throws {
    if !condition() { throw CameraError.invalid("self-test-\(name)") }
}
func rejects(_ name: String, _ operation: () throws -> Void) throws {
    do { try operation() } catch { return }
    throw CameraError.invalid("self-test-accepted-\(name)")
}
func selfTest() throws {
    let valid = Descriptor(type: builtinType, continuity: false, identity: "native-id")
    let external = Descriptor(type: "external", continuity: false, identity: "other")
    let continuity = Descriptor(type: builtinType, continuity: true, identity: "phone")
    let selected = try selectDevice([external, valid, continuity])
    try require(selected == 1, "selection-exact-index")
    for candidates in [[], [external], [continuity], [valid, valid],
                       [Descriptor(type: builtinType, continuity: false, identity: "")]] {
        try rejects("selection") { _ = try selectDevice(candidates) }
    }
    let padded: [UInt8] = [1,2,3,4,5,6,7,8,99,99,99,99,9,10,11,12,13,14,15,16,88,88,88,88]
    let packed = try padded.withUnsafeBytes { try packedRows($0, width: 2, height: 2, stride: 12) }
    try require(Array(packed) == Array(UInt8(1)...UInt8(16)), "row-padding")
    try rejects("short-row") { _ = try padded.withUnsafeBytes { try packedRows($0, width: 2, height: 2, stride: 4) } }
    try rejects("short-buffer") { _ = try padded.withUnsafeBytes { try packedRows($0, width: 2, height: 3, stride: 12) } }
    var encoder = WireEncoder()
    let payload = Data([1,2,3,4,5,6,7,8])
    let packet = try encoder.packet(payload, width: 2, height: 1, seconds: 0.0129)
    try require(Array(packet.prefix(12)) == [64,40,0,0,0,0,0,0,0,0,0,8], "big-endian-dI")
    try require(packet.dropFirst(12) == payload, "framing-payload")
    try rejects("wrong-size") { _ = try encoder.packet(Data([0]), width: 2, height: 1, seconds: 1) }
    try rejects("reconfiguration") { _ = try encoder.packet(payload, width: 1, height: 2, seconds: 1) }
    for seconds in [0.012, 0.011, -1, Double.nan, Double.infinity, 1e30] {
        try rejects("timestamps") { _ = try encoder.packet(payload, width: 2, height: 1, seconds: seconds) }
    }
    _ = try encoder.packet(payload, width: 2, height: 1, seconds: 0.013)
    try emitJSON(["status":"ok", "checks":["selection","row-padding","framing","reconfiguration","timestamps"], "camera_access":false])
}
func emitJSON(_ object: [String: Any]) throws {
    var data = try JSONSerialization.data(withJSONObject: object, options: [.sortedKeys])
    data.append(10)
    try FileHandle.standardOutput.write(contentsOf: data)
}
func discovery() throws -> (AVCaptureDevice, Descriptor) {
    // Discovery alone is metadata-only; never create a session in --discover.
    let devices = AVCaptureDevice.DiscoverySession(deviceTypes: [.builtInWideAngleCamera], mediaType: .video, position: .unspecified).devices
    let descriptors = devices.map { Descriptor(type: $0.deviceType.rawValue, continuity: $0.isContinuityCamera, identity: $0.uniqueID) }
    let index = try selectDevice(descriptors)
    return (devices[index], descriptors[index])
}
func identityDigest(_ descriptor: Descriptor) -> String {
    SHA256.hash(data: Data(descriptor.identity.utf8)).map { String(format: "%02x", $0) }.joined()
}
final class Receiver: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    let descriptor: Descriptor
    var encoder = WireEncoder()
    var sentHandshake = false
    init(_ descriptor: Descriptor) { self.descriptor = descriptor }
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        do {
            guard let buffer = CMSampleBufferGetImageBuffer(sampleBuffer),
                  CVPixelBufferGetPixelFormatType(buffer) == kCVPixelFormatType_32BGRA else { throw CameraError.invalid("non-BGRA-buffer") }
            CVPixelBufferLockBaseAddress(buffer, .readOnly)
            defer { CVPixelBufferUnlockBaseAddress(buffer, .readOnly) }
            guard let base = CVPixelBufferGetBaseAddress(buffer) else { throw CameraError.invalid("missing-buffer") }
            let width = CVPixelBufferGetWidth(buffer), height = CVPixelBufferGetHeight(buffer)
            let stride = CVPixelBufferGetBytesPerRow(buffer)
            let packed = try packedRows(UnsafeRawBufferPointer(start: base, count: CVPixelBufferGetDataSize(buffer)), width: width, height: height, stride: stride)
            let packet = try encoder.packet(packed, width: width, height: height, seconds: CMTimeGetSeconds(CMSampleBufferGetPresentationTimeStamp(sampleBuffer)))
            if !sentHandshake {
                try emitJSON(["protocol":1, "width":width, "height":height, "pixel_format":"BGRA", "frame_bytes":packed.count,
                              "device_type":descriptor.type, "continuity":descriptor.continuity, "device_sha256":identityDigest(descriptor)])
                sentHandshake = true
            }
            try FileHandle.standardOutput.write(contentsOf: packet)
        } catch { fail(error) }
    }
}
func fail(_ error: Error) -> Never {
    FileHandle.standardError.write(Data("native-camera: \(error)\n".utf8))
    exit(1)
}
do {
    let args = Array(CommandLine.arguments.dropFirst())
    if args == ["--self-test"] { try selfTest() }
    else if args == ["--discover"] {
        let (_, descriptor) = try discovery()
        try emitJSON(["device_type":descriptor.type, "continuity":descriptor.continuity, "device_sha256":identityDigest(descriptor)])
    } else if args.count == 2 && args[0] == "--capture", let duration = Double(args[1]), duration.isFinite, duration > 0, duration <= 300 {
        let (device, descriptor) = try discovery()
        guard AVCaptureDevice.authorizationStatus(for: .video) == .authorized else { throw CameraError.invalid("camera-permission-not-authorized; allow camera access for the launching application") }
        let session = AVCaptureSession()
        session.beginConfiguration()
        if session.canSetSessionPreset(.hd1280x720) { session.sessionPreset = .hd1280x720 }
        let input = try AVCaptureDeviceInput(device: device)
        guard session.canAddInput(input) else { throw CameraError.invalid("cannot-add-exact-input") }
        session.addInput(input)
        let output = AVCaptureVideoDataOutput()
        output.alwaysDiscardsLateVideoFrames = true
        output.videoSettings = [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA]
        let receiver = Receiver(descriptor)
        let queue = DispatchQueue(label: "owned.bgra.capture")
        output.setSampleBufferDelegate(receiver, queue: queue)
        guard session.canAddOutput(output) else { throw CameraError.invalid("cannot-add-output") }
        session.addOutput(output)
        if let connection = output.connection(with: .video), connection.isVideoMirroringSupported {
            connection.automaticallyAdjustsVideoMirroring = false
            connection.isVideoMirrored = false
        }
        session.commitConfiguration()
        session.startRunning()
        RunLoop.current.run(until: Date(timeIntervalSinceNow: duration))
        output.setSampleBufferDelegate(nil, queue: nil)
        session.stopRunning()
        withExtendedLifetime(receiver) {}
    } else { throw CameraError.invalid("usage: --self-test | --discover | --capture SECONDS(0,300]") }
} catch { fail(error) }
