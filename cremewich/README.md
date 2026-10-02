# Cremewich website

A static, single-page site for Cremewich: a poster-style hero with the whole
Nutella Marble Swirl sandwich, stickers and a spinning badge, a scrolling flavour
marquee, a tilted three-point feature row, the full menu (combos, ice cream
sandwiches and popsicles with ₹ prices, filterable), the "inner child" band,
our story and find-us/contact sections. Animations (wobbles, drips, scroll-in
reveals) switch off for visitors who prefer reduced motion. Product
photos in `images/` are cropped from the Cremewich brand posters. Plain HTML, CSS and JavaScript with no build step.

## Run it locally

Open `index.html` in a browser, or serve the folder:

```
cd cremewich
python3 -m http.server 8000
```

then visit http://localhost:8000.

## Updating the menu

Menu items, descriptions and prices are in the `#menu` section of
`index.html`, taken from the Cremewich Swiggy listing.

## Placeholders to replace

- Address, hours, email and Instagram handle in the contact section of `index.html`.
- The contact form only validates and shows a thank-you message; connect it
  to a backend or a form service (e.g. Formspree, Netlify Forms) to actually
  receive messages.
