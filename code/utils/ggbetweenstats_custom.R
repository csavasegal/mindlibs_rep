# Custom wrapper for ggbetweenstats with modified defaults
ggbetweenstats_custom <- function(data, x, y, ...) {
  ggstatsplot::ggbetweenstats(
    data = data,
    x = {{ x }},
    y = {{ y }},
    results.subtitle = FALSE,
    test.value = FALSE,   # 👈 add this
    bf.message = FALSE,
    centrality.point.args = list(size = 1, color = "black"),
    centrality.label.args = list(size = 0),
    ...
  )
}

