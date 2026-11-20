"""Fit-only coherent hm1588 sequence rotation; no invented observations."""
import numpy as np
from . import augmentation as historical


def validate_tensor(x):
    if (type(x) is not np.ndarray or x.dtype!=np.float32 or x.ndim!=3
            or x.shape[1:]!=(30,1588) or not np.isfinite(x).all()):
        raise ValueError('expected finite plain Float32[N,30,1588]')
    historical.validate_tensor(x[:,:,:153])
    if not np.isin(x[:,:,1587],[0,1]).all(): raise ValueError('invalid face mask')
    face=x[:,:,153:1587].reshape(len(x),30,478,3)
    if (face[x[:,:,1587]==0]!=0).any(): raise ValueError('absent face contamination')
    if not (x[:,:,1587]==1).all(): raise ValueError('eligible tensor requires present face')
    if not np.allclose(face[:,:,:,2].mean(axis=2,dtype=np.float64),0,atol=2e-6,rtol=0):
        raise ValueError('invalid face mean-relative depth (tolerance 2e-6)')


def rotate_fit(x,source_ids,*,partition,seed=20260705):
    validate_tensor(x)
    prefix,receipt=historical.rotate_fit(x[:,:,:153],source_ids,partition=partition,seed=seed)
    out=x.copy(); out[:,:,:153]=prefix
    for i,angle in enumerate(receipt['angles_degrees']):
        theta=np.deg2rad(angle)
        matrix=np.array([[np.cos(theta),np.sin(theta)],[-np.sin(theta),np.cos(theta)]])
        face=out[i,:,153:1587].reshape(30,478,3)
        present=out[i,:,1587]==1
        face[present,:,:2]=face[present,:,:2]@matrix
    receipt['policy']='one_per_original_sequence_coherent_hand_pose_face_xy_uniform_degrees_[-5,5]'
    return out,receipt
