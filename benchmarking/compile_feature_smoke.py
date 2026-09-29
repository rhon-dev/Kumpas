#!/usr/bin/env python3
"""Compile and run pure Kotlin feature smoke without an Android SDK."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path.home() / ".gradle/caches/modules-2/files-2.1"
OUT = Path.home() / ".hermes/cache/scratch/kumpas-kotlin-test"
PATTERNS = ("kotlin-compiler-embeddable-2.0.21.jar", "kotlin-stdlib-2.0.21.jar",
            "kotlin-script-runtime-2.0.21.jar", "kotlin-reflect-2.0.21.jar",
            "trove4j-*.jar", "kotlinx-coroutines-core-jvm-1.8.0.jar",
            "annotations-23.0.0.jar")


def main():
    jars = [next(CACHE.rglob(pattern)) for pattern in PATTERNS]
    OUT.mkdir(parents=True, exist_ok=True)
    smoke = ROOT / "benchmarking/kotlin/FeatureNormalizerSmoke.kt"
    normalizer = ROOT / "app/android/app/src/main/kotlin/com/kumpas/kumpas_app/FeatureNormalizer.kt"
    sources = [str(smoke)] + ([str(normalizer)] if normalizer.exists() else [])
    compile_cmd = ["java", "-cp", ":".join(map(str, jars)),
                   "org.jetbrains.kotlin.cli.jvm.K2JVMCompiler", "-no-stdlib",
                   "-classpath", str(jars[1]), "-d", str(OUT), *sources]
    subprocess.run(compile_cmd, check=True)
    subprocess.run(["java", "-cp", f"{OUT}:{jars[1]}",
                    "com.kumpas.kumpas_app.FeatureNormalizerSmokeKt"], check=True)


if __name__ == "__main__":
    main()
