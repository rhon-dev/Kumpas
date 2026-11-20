"""Explicit synthetic hm1588 geometry; no source tensors."""
import importlib
import importlib.util
import numpy as np
import pytest
from .test_augmentation import synthetic_tensor as prefix


def augmentation():
    name='training.holistic_migration.face_augmentation'
    return importlib.import_module(name if importlib.util.find_spec(name) else 'training.holistic_migration.augmentation')


def synthetic_tensor(n=2):
    x=np.zeros((n,30,1588),np.float32)
    x[:,:,:153]=prefix(n)
    face=x[:,:,153:1587].reshape(n,30,478,3)
    face[:,:,:,:2]=np.arange(956,dtype=np.float32).reshape(478,2)/1000
    face[:,:,:,2]=np.linspace(-.1,.1,478,dtype=np.float32)
    x[:,:,1587]=1
    return x


def test_coherent_rotation_preserves_depth_masks_and_absence():
    a=augmentation(); x=synthetic_tensor(); before=x.copy()
    out,receipt=a.rotate_fit(x,['synthetic/a','synthetic/b'],partition='fit')
    assert out.shape==(2,30,1588)
    np.testing.assert_array_equal(x.view(np.uint32),before.view(np.uint32))
    for i,angle in enumerate(receipt['angles_degrees']):
        theta=np.deg2rad(angle); matrix=np.array([[np.cos(theta),np.sin(theta)],[-np.sin(theta),np.cos(theta)]])
        np.testing.assert_allclose(out[i,:,153:1587].reshape(30,478,3)[:,:,:2],x[i,:,153:1587].reshape(30,478,3)[:,:,:2]@matrix,atol=1e-7)
        np.testing.assert_array_equal(out[i,:,155:1587:3],x[i,:,155:1587:3])
        for start,mask in [(0,150),(63,151)]:
            b=x[i,:,start:start+63].reshape(30,21,3); actual=out[i,:,start:start+63].reshape(30,21,3)
            present=x[i,:,mask]==1
            np.testing.assert_allclose(actual[present,:,:2],b[present,:,:2]@matrix,atol=1e-7)
            np.testing.assert_array_equal(actual[:,:,2],b[:,:,2])
            np.testing.assert_array_equal(actual[~present],b[~present])
        pose=x[i,:,126:150].reshape(30,6,4); actual=out[i,:,126:150].reshape(30,6,4)
        visible=pose[:,:,3]>=.5
        np.testing.assert_allclose(actual[:,:,:2][visible],pose[:,:,:2][visible]@matrix,atol=1e-7)
        np.testing.assert_array_equal(actual[:,:,2:],pose[:,:,2:])
        np.testing.assert_array_equal(actual[~visible],pose[~visible])
    np.testing.assert_array_equal(out[:,:,150:153],x[:,:,150:153])
    np.testing.assert_array_equal(out[:,:,1587],x[:,:,1587])
    assert all(-5<=v<=5 for v in receipt['angles_degrees'])
    assert receipt['source_ids']==['synthetic/a','synthetic/b'] and receipt['real_observations_added']==0
    again,r=a.rotate_fit(x[::-1].copy(),['synthetic/b','synthetic/a'],partition='fit')
    np.testing.assert_array_equal(again,out[::-1]); assert r['angles_degrees']==receipt['angles_degrees'][::-1]


@pytest.mark.parametrize('bad',['face_mask','missing_face','face_depth','nonfinite','shape','dtype','shoulders','hand','invisible'])
def test_tensor_invariants(bad):
    a=augmentation(); x=synthetic_tensor()
    if bad=='face_mask': x[0,0,1587]=.5
    if bad=='missing_face': x[0,0,1587]=0
    if bad=='face_depth': x[0,0,155]+=.1
    if bad=='nonfinite': x[0,0,200]=np.nan
    if bad=='shape': x=x[:,:,:153]
    if bad=='dtype': x=x.astype(np.float64)
    if bad=='shoulders': x[0,0,126]=10
    if bad=='hand': x[0,0,0]=1; x[0,0,150]=0
    if bad=='invisible': x[0,0,138]=1; x[0,0,141]=0
    with pytest.raises(ValueError): a.validate_tensor(x)


@pytest.mark.parametrize('partition',['validation','test','tiny-fit'])
def test_rotation_refuses_nonfit(partition):
    with pytest.raises(ValueError): augmentation().rotate_fit(synthetic_tensor(),['a','b'],partition=partition)
