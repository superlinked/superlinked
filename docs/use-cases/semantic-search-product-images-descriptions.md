---
description: Learn about fundamental concepts of Superlinked.
icon: magnifying-glass
---

# Semantic Search - Product Images & Descriptions


This use-case notebook shows semantic search in fashion images for e-commerce. 

In e-commerce, being able to serve user queries with the most relevant results is of utmost importance. Users predominantly use text to describe what they would like and that poses a problem e-commerce websites face: products generally lack extensive textual information. However, there is no better way to describe a product than an image. Luckily, researchers also realised that, and came up with multi-modal Vision Transformers that embed text and images in the same space, thereby making us able to search with text in images of products. Namely, searching for an "elegant dress" does not require the description to contain anything similar to return the actual elegant dresses.

To demonstrate that, we are going to perform search in a fashion dataset consinsting of images with short descriptions. We will be able to search:
- with text in the descriptions,
- with text in the images,
- with an image in the images

or we can combine these in the following ways:
- search with the same or different text in the descriptions and the images
- search with text in the descriptions, and with images in the images

we will show that multi-modal search in the text embedding AND the image embedding space is the best approach to get the most relevant results.

### Follow along in this Colab

{% embed url="https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/image_search_e_commerce.ipynb" %}
{% endembed %}