#!/bin/sh
set -eu

ALIAS=local
BUCKET=posters

until mc alias set "$ALIAS" "$MINIO_URL" "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null 2>&1; do
    echo "waiting for minio at $MINIO_URL..."
    sleep 2
done

mc mb --ignore-existing "$ALIAS/$BUCKET"

mc anonymous set download "$ALIAS/$BUCKET"

POLICY_FILE=/tmp/admin-panel-policy.json
cat > "$POLICY_FILE" <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:DeleteObject", "s3:GetObject", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::$BUCKET", "arn:aws:s3:::$BUCKET/*"]
    }
  ]
}
EOF

if mc admin user svcacct info "$ALIAS" "$ADMIN_PANEL_ACCESS_KEY" >/dev/null 2>&1; then
    echo "service account $ADMIN_PANEL_ACCESS_KEY already exists, skipping."
else
    mc admin user svcacct add "$ALIAS" "$MINIO_ROOT_USER" \
        --access-key "$ADMIN_PANEL_ACCESS_KEY" \
        --secret-key "$ADMIN_PANEL_SECRET_KEY" \
        --policy "$POLICY_FILE"
    echo "created service account $ADMIN_PANEL_ACCESS_KEY."
fi

echo "minio provisioning complete."
