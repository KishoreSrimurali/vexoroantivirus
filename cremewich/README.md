# Cremewich website

A static, single-page site for Cremewich: hero, flavours (with a filterable
list), a stock-up band, our story, and find-us/contact sections. Product
photos in `images/` are cropped from the Cremewich brand posters. Plain HTML, CSS and JavaScript with no build step.

## Run it locally

Open `index.html` in a browser, or serve the folder:

```
cd cremewich
python3 -m http.server 8000
```

then visit http://localhost:8000.

## Placeholders to replace

- Address, hours, email and Instagram handle in the contact section of `index.html`.
- The six boxed flavours below the two signatures (Nutella Marble Swirl and
  PB + Chocolate come from the brand images; the rest are placeholders).
- Prices, if you want them on the page.
- The contact form only validates and shows a thank-you message; connect it
  to a backend or a form service (e.g. Formspree, Netlify Forms) to actually
  receive messages.
