"""Explicit synthetic hm153 augmentation fixtures; no media or canonical source data."""
import importlib
import numpy as np
import pytest


def synthetic_tensor(n=2):
    x=np.zeros((n,30,153),np.float32)
    x[:,:,:63]=np.arange(63,dtype=np.float32)/31
    x[:,:,63:126]=np.arange(63,dtype=np.float32)[::-1]/19
    x[:,:,2]=0; x[:,:,65]=0
    pose=x[:,:,126:150].reshape(n,30,6,4)
    pose[:]=[.2,-.3,.125,.9]
    pose[:,:,0]=[-.5,0,-.2,1]
    pose[:,:,1]=[.5,0,.2,1]
    x[:,:,150:]=1
    x[:,0,:63]=0; x[:,0,150]=0
    x[:,1,63:126]=0; x[:,1,151]=0
    x[:,2,:126]=0; x[:,2,150:152]=0
    pose[:,3,4]=0
    return x


def test_fit_rotation_preserves_missing_masks_depth_and_one_angle():
    a=importlib.import_module('training.holistic_migration.augmentation')
    x=synthetic_tensor(); before=x.copy()
    out,receipt=a.rotate_fit(x,['synthetic/a','synthetic/b'],partition='fit',seed=20260705)
    np.testing.assert_array_equal(x,before)
    assert not np.shares_memory(x,out)
    np.testing.assert_array_equal(out[:,:,150:],x[:,:,150:])
    np.testing.assert_array_equal(out[:,:,:126].reshape(2,30,42,3)[:,:,:,2],x[:,:,:126].reshape(2,30,42,3)[:,:,:,2])
    np.testing.assert_array_equal(out[:,:,126:150].reshape(2,30,6,4)[:,:,:,2:],x[:,:,126:150].reshape(2,30,6,4)[:,:,:,2:])
    assert np.all(out[:,0,:63]==0) and np.all(out[:,1,63:126]==0) and np.all(out[:,2,:126]==0)
    assert np.all(out[:,3,142:146]==0)
    assert receipt['derived_count']==2 and receipt['source_ids']==['synthetic/a','synthetic/b']
    assert receipt['real_observations_added']==0
    assert all(-5<=v<=5 for v in receipt['angles_degrees'])
    for i,angle in enumerate(receipt['angles_degrees']):
        theta=np.deg2rad(angle); matrix=np.array([[np.cos(theta),np.sin(theta)],[-np.sin(theta),np.cos(theta)]])
        np.testing.assert_allclose(out[i,4:,:63].reshape(26,21,3)[:,:,:2],x[i,4:,:63].reshape(26,21,3)[:,:,:2]@matrix,rtol=2e-6,atol=1e-7)
        shoulders=out[i,:,126:134].reshape(30,2,4)[:,:,:2]
        np.testing.assert_allclose(shoulders.mean(axis=1),0,atol=1e-7)
        np.testing.assert_allclose(np.linalg.norm(shoulders[:,0]-shoulders[:,1],axis=1),1,atol=1e-7)
    again,r=a.rotate_fit(x,['synthetic/a','synthetic/b'],partition='fit',seed=20260705)
    np.testing.assert_array_equal(out,again); assert r==receipt
    assert not np.array_equal(out[:,:,:2],x[:,:,:2])


@pytest.mark.parametrize('partition',['validation','test','train',None])
def test_rotation_refuses_non_fit(partition):
    a=importlib.import_module('training.holistic_migration.augmentation')
    with pytest.raises(ValueError): a.rotate_fit(synthetic_tensor(),['a','b'],partition=partition)


@pytest.mark.parametrize('bad',['dtype','shape','nan','mask','absent','invisible','pose_mask','wrist_depth','shoulder','ids','seed'])
def test_invalid_tensor_or_identity_refused(bad):
    a=importlib.import_module('training.holistic_migration.augmentation')
    x=synthetic_tensor(); ids=['a','b']; seed=20260705
    if bad=='dtype': x=x.astype(np.float64)
    if bad=='shape': x=x[:,:,:152]
    if bad=='nan': x[0,4,0]=np.nan
    if bad=='mask': x[0,4,150]=.5
    if bad=='absent': x[0,0,0]=.1
    if bad=='invisible': x[0,3,142]=.1
    if bad=='pose_mask': x[0,4,152]=0
    if bad=='wrist_depth': x[0,4,2]=.1
    if bad=='shoulder': x[0,4,126]=.1
    if bad=='ids': ids=['a','a']
    if bad=='seed': seed=True
    with pytest.raises(ValueError): a.rotate_fit(x,ids,partition='fit',seed=seed)

