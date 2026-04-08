# GitHub Actions CI/CD

Repo này dùng GitHub Actions cho `CI`, còn `CD` hiện nên dựa vào Git integration của `Railway` và `Vercel`.

## 1. Những gì đã có trong repo

- Workflow CI: `.github/workflows/ci.yml`
- Khi có `push` hoặc `pull_request` vào `main`, workflow sẽ:
  - cài backend dependencies
  - chạy `pytest`
  - cài frontend dependencies
  - chạy `npm run build` trong `frontend/`

## 2. Vì sao không cần redeploy tay nữa

Sau khi kết nối GitHub:

- `Railway` sẽ tự deploy khi branch `main` có commit mới
- `Vercel` cũng sẽ tự deploy khi branch `main` có commit mới

Tức là flow chuẩn sẽ là:

1. sửa code local
2. `git add`
3. `git commit`
4. `git push origin main`
5. GitHub Actions chạy CI
6. Railway và Vercel tự nhận commit mới và deploy

## 3. Cấu hình Railway để chỉ deploy sau khi CI pass

Trong Railway service:

1. vào `Settings`
2. bật `Wait for CI`

Khi bật mục này, Railway sẽ đợi GitHub check của workflow `CI` thành công rồi mới deploy.

## 4. Cấu hình Vercel

Vercel hiện đã tự deploy khi repo có commit mới. Bạn chỉ cần giữ:

- repo kết nối đúng
- branch production là `main`
- env `VITE_API_BASE_URL` đã được set

Lưu ý:

- đổi `Environment Variables` trên Vercel vẫn cần một lần redeploy
- sau đó các commit code tiếp theo sẽ tự deploy

## 5. Nếu muốn Vercel chỉ deploy sau khi CI pass

Vercel mặc định deploy theo Git push. Nếu muốn kiểm soát chặt hơn:

1. tạo `Deploy Hook` trong Vercel
2. lưu hook URL vào GitHub secret, ví dụ:
   - `VERCEL_DEPLOY_HOOK_URL`
3. thêm workflow riêng gọi hook đó sau khi workflow `CI` thành công

Hiện repo chưa bật cách này để tránh deploy kép, vì Vercel đang auto deploy từ Git rồi.

## 6. Những secret bạn không cần đặt trong GitHub Actions hiện tại

Workflow CI hiện không cần:

- `DATABASE_URL`
- `VITE_API_BASE_URL` production thật
- token Railway
- token Vercel

Nó chỉ kiểm tra:

- backend có chạy test được không
- frontend có build được không

## 7. Khuyến nghị vận hành

- dùng `main` làm branch deploy
- mọi thay đổi đều push qua GitHub
- không chỉnh tay trực tiếp trên Railway/Vercel trừ biến môi trường
- nếu đổi env production, redeploy một lần rồi tiếp tục dùng auto deploy
