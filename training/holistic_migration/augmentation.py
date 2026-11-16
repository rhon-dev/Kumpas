"""Experimental fit-only, mask-preserving sequence XY rotation (not linguistic validation)."""
import hashlib
import numpy as np


def validate_tensor(x):
    """Check canonical packed feature invariants without altering channels."""
    if (type(x) is not np.ndarray or x.dtype!=np.float32 or x.ndim!=3
            or x.shape[1:]!=(30,153) or not np.isfinite(x).all()):
        raise ValueError('expected finite plain Float32[N,30,153]')
    if not np.isin(x[:,:,150:],[0,1]).all() or not (x[:,:,152]==1).all():
        raise ValueError('invalid masks or unusable pose')
    for start,mask in [(0,150),(63,151)]:
        if (x[:,:,start:start+63][x[:,:,mask]==0]!=0).any():
            raise ValueError('absent hand block contamination')
        if (x[:,:,start+2]!=0).any(): raise ValueError('hand wrist-local depth invalid')
    pose=x[:,:,126:150].reshape(len(x),30,6,4)
    visibility=pose[:,:,:,3]
    if (visibility<0).any() or (visibility>1).any() or (pose[visibility<.5]!=0).any():
        raise ValueError('invisible pose contamination/invalid visibility')
    shoulders=pose[:,:,:2,:]
    if (shoulders[:,:,:,3]<.5).any(): raise ValueError('unusable shoulders')
    if (not np.allclose(shoulders[:,:,:,:3].mean(axis=2),0,atol=2e-6,rtol=0)
            or not np.allclose(np.linalg.norm(shoulders[:,:,0,:2]-shoulders[:,:,1,:2],axis=2),1,atol=2e-6,rtol=0)):
        raise ValueError('invalid shoulder midpoint/2D scale')


def rotate_fit(x, source_ids, *, partition, seed=20260705):
    """Return exactly one independently seeded copy per fit original, never mutate input."""
    if partition!='fit': raise ValueError('augmentation is fit-only')
    validate_tensor(x)
    if (type(seed) is not int or seed<0 or len(source_ids)!=len(x)
            or any(type(s) is not str or not s for s in source_ids)
            or len(set(source_ids))!=len(source_ids)):
        raise ValueError('invalid rotation seed/source IDs')
    out=x.copy()
    angles=[]
    for i,source in enumerate(source_ids):
        key=hashlib.sha256(f'{seed}:{source}'.encode()).digest()
        angle=float(np.random.default_rng(int.from_bytes(key[:8],'big')).uniform(-5,5))
        angles.append(angle)
        theta=np.deg2rad(angle)
        matrix=np.array([[np.cos(theta),np.sin(theta)],[-np.sin(theta),np.cos(theta)]])
        for start,mask in [(0,150),(63,151)]:
            block=out[i,:,start:start+63].reshape(30,21,3)
            present=out[i,:,mask]==1
            block[present,:,:2]=block[present,:,:2]@matrix
        pose=out[i,:,126:150].reshape(30,6,4)
        usable=(pose[:,:,3]>=.5)&(out[i,:,152,None]==1)
        pose[:,:,:2][usable]=pose[:,:,:2][usable]@matrix
    return out,dict(seed=seed,policy='one_per_original_sequence_xy_uniform_degrees_[-5,5]',
                    source_ids=list(source_ids),angles_degrees=angles,derived_count=len(x),
                    real_observations_added=0,partition='fit')
