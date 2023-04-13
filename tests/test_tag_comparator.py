import pytest

from taggerresults import TaggerResults
import tag_comparator

@pytest.fixture
def one_label():
    results = TaggerResults()

    results.save_label("image1", "service1", "cat", 1, 1)

    results.save_label("image1", "service2", "dog", 1, 1)
    results.save_label("image1", "service2", "car", 1, 1)
    results.save_label("image1", "service2", "kitten", 1, 1)

    return results

@pytest.fixture
def two_labels():
    results = TaggerResults()

    results.save_label("image1", "service1", "cat", 1, 1)
    results.save_label("image1", "service1", "kitten", 1, 1)

    results.save_label("image1", "service2", "dog", 1, 1)
    results.save_label("image1", "service2", "car", 1, 1)
    results.save_label("image1", "service2", "kitten", 1, 1)

    return results

@pytest.fixture
def two_images():
    results = TaggerResults()

    results.save_label("image1", "service1", "cat", 1, 1)

    results.save_label("image1", "service2", "dog", 1, 1)
    results.save_label("image1", "service2", "car", 1, 1)
    results.save_label("image1", "service2", "kitten", 1, 1)

    results.save_label("image2", "service1", "cat", 1, 1)

    results.save_label("image2", "service2", "car", 1, 1)
    results.save_label("image2", "service2", "kitten", 1, 1)

    return results

def test_compare_tags_simple_identity( one_label ):
    results = tag_comparator.compare_tags( one_label, "service1", "service2", tag_comparator.identity_comparator )
    assert len( results.keys() ) == 1
    assert len( results['cat'] ) == 1
    assert results['cat'][0] == 0

def test_compare_tags_simple_w2v( one_label ):
    results = tag_comparator.compare_tags( one_label, "service1", "service2", tag_comparator.w2v_comparator )
    assert 0.760 <= results['cat'][0] <= 0.761 ## our paper used rounded values on the manual inspection

def test_compare_tags_simple_identity( two_labels ):
    results = tag_comparator.compare_tags( two_labels, "service1", "service2", tag_comparator.identity_comparator )
    assert len( results.keys() ) == 2
    assert len( results['cat'] ) == 1
    assert len( results['kitten'] ) == 1
    assert results['cat'][0] == 0
    assert results['kitten'][0] == 1

def test_compare_tags_two_images_w2v( two_images ):
    results = tag_comparator.compare_tags( two_images, "service1", "service2", tag_comparator.w2v_comparator )
    assert 0.760 <= results['cat'][0] <= 0.762 ## our paper used rounded values on the manual inspection
    assert 0.745 <= results['cat'][1] <= 0.747 ## our paper used rounded values on the manual inspection