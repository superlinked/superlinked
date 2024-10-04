---
description: Learn about fundamental concepts of Superlinked.
icon: cart-shopping
---

# RecSys - Ecommerce

In this example, we are building a recommender system for an e-commerce site mainly selling clothing.

Here are the details about the products we know:
- price
- the number of reviewers
- their rating
- textual description
- name of the product (usually contains the brand name)
- category
    
We have two users, and each of them can be either be characterised by
- the initial choice of a product offered to them at registration.
- or more general characteristics explained in the below paragraph (price, reviews)
   
Users have preferences on the textual characteristics of products (description, name, category), and according to classical economics, ceteris paribus prefers products 
- that cost less
- has a lot of reviews
- with higher ratings
so we are going to set our spaces up to reflect that.

In the second part of the notebook, we introduce behavioral data in the form of events and their effects. 

Let's imagine we first examine a cold-start setup - we try to recommend items for users we know very little of. 

After introducing user behavioral data in the form of events, we look at users with some history on our site: clicked on products, bought others, etc. These are taken into account to improve the quality of the recommendations.

### Follow along in this Colab

{% embed url="https://colab.research.google.com/github/superlinked/superlinked/blob/main/notebook/recommendations_e_commerce.ipynb" %}
{% endembed %}