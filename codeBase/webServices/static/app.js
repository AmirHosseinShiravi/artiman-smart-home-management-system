

page('*', parse)
page('/', show)
page()

function parse(ctx, next) {
  ctx.query = qs.parse(location.search.slice(1));
  console.log(ctx.query)
  // next();
}

function show(ctx) {
  if (Object.keys(ctx.query).length) {
    document
      .querySelector('pre')
      .textContent = JSON.stringify(ctx.query, null, 2);
  }
}