FROM nginx:alpine

COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# No site data is baked into the image - it's bind-mounted at runtime
# (see docker-compose.yml), so the same image can serve /tmp/bmw_wds_12
# after any re-run of the preprocessing scripts without rebuilding.
