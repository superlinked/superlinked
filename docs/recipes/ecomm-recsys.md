---
icon: cart-shopping
---

# Ecommerce Recsys demo

{% hint style="info" %}
🚀 Try it out: [e-commerce-recsys-recipe.superlinked.io](https://e-commerce-recsys-recipe.superlinked.io)
⭐ Give us a star: [Superlinked repo](https://links.superlinked.com/recsys_demo)
{% endhint %}

## Overview

In modern retail and e-commerce websites, personalized and immediate product recommendations can significantly boost customer engagement and drive sales conversions. In this demo, we showcase an example of such a website that uses Superlinked's ability to do real time recommendations. When a user lands on the store’s website, they are greeted by a web interface displaying various products. As they move around the page, whether clicking product details, scrolling through suggested items, or switching categories, every interaction is tracked in real time. 

These live signals help build a continuously updated profile of the user’s current interests. The system then quickly refreshes its recommendations to reflect the user’s changing intrests, so new and similar items appear without delay. This approach allows retailers to show the right products at the right time, enhancing the shopping experience and increasing the likelihood of a purchase. 

Additionally, we use [item2vec](https://arxiv.org/vc/arxiv/papers/1603/1603.04259v2.pdf) which introduces a collaborative aspect by capturing product relationships from collective user interactions. All of these approaches showcase how we can leverage Superlinked in an e-commerce application to deliver real-time, session-based recommendations. It is adaptable to your own product data as well, so you can tailor this setup to your specific product relationships and consumer behaviour. 

# How does it work ?

The user events reach a Wrapper API, which sits on top of the main Superlinked server. It:
-  Records which products users click or view.
-  Builds and updates a live session context that captures the user’s evolving interests.
-  Fetches updated recommendations from the vector database (e.g., Redis) based on these interactions.

Under the hood, the Superlinked server connects to a vector database (Redis in this example). Each product is stored with multi-modal embeddings that include images, descriptions, categories, and numeric properties.

# Item2vec

To enhance these recommendations, the system leverages an item2vec model trained on user event data. For instance, if many shoppers who click Product A also end up exploring Product B, item2vec embeddings capture that relationship, increasing B’s rank when someone else shows interest in A. You can train your own item2vec model using the provided scripts and adapt it to your data.

#  Real-Time Session-Based Recommendations

As the user continues to click and browse, the system instantly:
-  Updates the session context in the Wrapper API.
-  Runs fresh queries to the vector database with each new interaction.
-  Sends back updated recommendations to the UI, so the user sees new suggestions without reloading the page.

If the user starts exploring a particular category, brand, or price range, the system tailors the recommended items accordingly, keeping the shopping experience engaging and personalized. Because the system processes events as they happen, shoppers get the sense that the site is learning their preferences in real time. Highly relevant products show up first, while items that are somewhat related appear further down. This approach can boost engagement and sales, as visitors are guided toward products that align with their interests.


{% hint style="info" %}
🚀 Try it out: [e-commerce-recsys-recipe.superlinked.io](https://e-commerce-recsys-recipe.superlinked.io)
⭐ Give us a star: [Superlinked repo](https://links.superlinked.com/recsys_demo)
{% endhint %}

<!-- Link to the public repo (which we don't have for hotel search I think)
{% hint style="info" %}
💻 Github repo: [here](https://github.com/superlinked/superlinked-recipes/tree/main/projects/hotel-search)
{% endhint %} -->
