# Cremewich website

A static, single-page site for Cremewich: full-bleed hero, a three-point
feature row, the full menu (combos, ice
cream sandwiches and popsicles with ₹ prices, filterable), alternating story sections, and find-us/contact sections. Product
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
