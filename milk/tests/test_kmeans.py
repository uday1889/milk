import numpy as np
import milk.unsupervised
from milk.unsupervised.kmeans import assign_centroids, repeated_kmeans

def test_kmeans():
    np.random.seed(132)
    features = np.r_[np.random.rand(20,3)-.5,.5+np.random.rand(20,3)]
    def test_distance(dist, kwargs={}):
        centroids, _ = milk.unsupervised.kmeans(features, 2, distance=dist, **kwargs)
        positions = [0]*20 + [1]*20
        correct = (centroids == positions).sum()
        assert correct >= 38 or correct <= 2
    yield test_distance, 'euclidean'
    yield test_distance, 'seuclidean'
    yield test_distance, 'mahalanobis', { 'icov' : np.eye(3) }

def test_kmeans_centroids():
    np.random.seed(132)
    features = np.random.rand(201,30)
    for k in [2,3,5,10]:
        indices,centroids = milk.unsupervised.kmeans(features, k)
        for i in xrange(k):
            if np.any(indices == i):
                assert np.allclose(centroids[i], features[indices == i].mean(0))


def test_assign_cids():
    from milksets.wine import load
    features,_ = load()
    assigns, centroids = milk.unsupervised.kmeans(features, 3, R=2, max_iters=10)
    assert np.all(assign_centroids(features, centroids) == assigns)

def test_non_contiguous_fmatrix():
    from milksets.wine import load
    features,_ = load()
    features = features[:,::2]
    assigns, centroids = milk.unsupervised.kmeans(features, 3, R=2, max_iters=10)
    assert np.all(assign_centroids(features, centroids) == assigns)

    features = features.astype(np.int32)
    assigns, centroids = milk.unsupervised.kmeans(features, 3, R=2, max_iters=10)
    assert np.all(assign_centroids(features, centroids) == assigns)


def test_repeated_kmeans():
    np.random.seed(132)
    features = np.random.rand(201,30)
    cids,cs = repeated_kmeans(features, 3, 2)
    assert len(cids) == len(features)

def test_kmeans_return_partial():
    np.random.seed(132)
    features = np.r_[np.random.rand(20,3)-.5,.5+np.random.rand(20,3)]
    assignments,centroids = milk.unsupervised.kmeans(features, 2, R=129)
    centroids_ = milk.unsupervised.kmeans(features, 2, R=129, return_assignments=False)
    assignments_ = milk.unsupervised.kmeans(features, 2, R=129, return_centroids=False)
    assert np.all(centroids == centroids_)
    assert np.all(assignments == assignments_)



def test_kmeans_all_equal():
    import milk.unsupervised._kmeans
    np.random.seed(132)
    for _ in xrange(8):
        a = (np.random.random(1024*128)*250).astype(int)
        b = a.copy()
        assert milk.unsupervised._kmeans.are_equal(a,b)
        a[3435] += 1
        assert not milk.unsupervised._kmeans.are_equal(a,b)
