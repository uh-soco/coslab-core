# Cross-service Laber Agreement Score

Image recognition services provide different labels for the same images, 
with differences broadly either being different word choices for the same 
concept or not seeing same objects on both images.
Cross-service Laber Agreement Score (COSLAB) is a method to evaluate the 
semantic similarity on image labels across several image recognition 
systems.
It first produces each image a set of labels, one for each service.
Then it uses word embedding models to find the closest match across label 
sets to see how much cross-service agreement there are for each label.

## Conceptual how to use

Our work further highlights that image recognition services differ on what 
they see on images.
Due to this, we suggest approaching them as **interprentations** instead 
of objective truths.
In response, we propose two different strategies which you can employ to 
use them in your research:

1. Inclusive strategy: to ensure that your work takes different 
interprentations into account, use more than one image recognition service 
to label the images.
Then merge all labels together and acknowldge that results have inheritent 
differences emerging from different services.
1. Rigorous strategy: to ensure that your work takes different 
interprentations into account, use more than one image recognition service 
to label the images.
Then use COSLAB to choose only labels above a pre-defined threshold level 
for further analysis.

## Example

```
from coslab import aws
from coslab import googlecloud
from coslab import azure_vision
from coslab import taggerresults
from coslab import tag_comparator

## establishing a container for all results
results = taggerresults.TaggerResults()

## establish classifiers
amazon = aws.AWS(api_id="", api_key="", api_region="")
google = googlecloud.GoogleCloud(service_account_info="")
azure = azure_vision.Azure(subscription_key="", endpoint="")

amazon.process_local( results, "image.png")
google.process_local( results, "image.png")
azure.process_local( results, "image.png")

results.export_pickle("image.pickle")

tag_comparator.compare_data( results )
```

## Installation

COSLAB is available [via Pypi](https://pypi.org/project/coslab-core/), so you can

```
python3 -m pip install coslab-core
```

# References

* [Berg, A., & Nelimarkka, M. (2023). Do you see what I see? Measuring the 
semantic differences in image‐recognition services' outputs. _Journal of 
the Association for Information Science and 
Technology._](https://asistdl.onlinelibrary.wiley.com/doi/full/10.1002/asi.24827)
* [Nelimarkka, M., & Berg, A. (2023). Is the World Different Depending on 
Whose AI Is Looking at It? Comparing Image Recognition Services for Social 
Science Research. _Information Matters_, 
3(8).](https://informationmatters.org/2023/08/is-the-world-different-depending-on-whose-ai-is-looking-at-it-comparing-image-recognition-services-for-social-science-research/) 

# Applications

* None yet. Please let us know if you use it.

# Acknowledgments

We generiously thank C. V. Åkerlund Foundation for supporting this work.
