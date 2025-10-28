# Design Guidelines - Bot Giao dịch Tiền điện tử

## 📐 Quy trình Thiết kế với Figma

### 1. Thiết lập Figma Project

**Link Figma:** [Thêm link Figma của bạn vào đây]

**Thành viên:** 
- Designer: [Tên thành viên]
- Reviewers: [Tên các thành viên khác]

### 2. Cấu trúc File Figma

```
Crypto Trading Bot
├── 🎨 Design System
│   ├── Colors
│   ├── Typography
│   ├── Icons
│   └── Components
├── 📱 Screens
│   ├── Dashboard
│   ├── Trading Control
│   ├── Chart View
│   └── Settings
└── 🔄 Prototypes
```

### 3. Quy trình Export và Update

#### Bước 1: Thiết kế trên Figma
- Tạo/chỉnh sửa thiết kế trên Figma
- Đặt tên frame rõ ràng (VD: `Dashboard-v1.0`, `TradingControl-v1.1`)
- Review với team trước khi export

#### Bước 2: Export từ Figma

**Export file .fig:**
1. File → Save as .fig
2. Đặt tên theo format: `CryptoBot-Design-YYYY-MM-DD.fig`
3. Lưu vào thư mục `design/figma-files/`

**Export Assets:**
- Icons: SVG format → `design/assets/icons/`
- Images: PNG/JPG → `design/assets/images/`
- Components: SVG → `design/assets/components/`

**Export Screenshots:**
- Export preview các screens → `design/screenshots/`
- Format: PNG, Resolution: 1920x1080

#### Bước 3: Commit lên GitHub

```bash
# Thêm file vào git
git add design/

# Commit với message rõ ràng
git commit -m "design: update dashboard layout v1.2"

# Push lên GitHub
git push origin main
```

### 4. Naming Convention

#### File Figma:
```
CryptoBot-Design-YYYY-MM-DD.fig
VD: CryptoBot-Design-2025-10-28.fig
```

#### Screenshots:
```
[ScreenName]-v[Version]-YYYY-MM-DD.png
VD: Dashboard-v1.0-2025-10-28.png
```

#### Assets:
```
[category]-[name]-[size].svg
VD: icon-chart-24.svg, logo-binance-48.svg
```

### 5. Design System

#### Colors
```
Primary: #F0B90B (Binance Yellow)
Secondary: #1E2026 (Dark Background)
Success: #0ECB81 (Green - Profit)
Danger: #F6465D (Red - Loss)
Background: #0B0E11
Surface: #1E2329
Text Primary: #EAECEF
Text Secondary: #848E9C
```

#### Typography
```
Font Family: Inter, -apple-system, sans-serif
Heading 1: 32px, Bold
Heading 2: 24px, Semibold
Body: 16px, Regular
Caption: 14px, Regular
Small: 12px, Regular
```

#### Spacing
```
xs: 4px
sm: 8px
md: 16px
lg: 24px
xl: 32px
xxl: 48px
```

### 6. Components cần thiết

- [ ] Header / Navigation
- [ ] Trading Chart (Candlestick)
- [ ] Order Book Display
- [ ] Balance Card
- [ ] Trading Control Panel
- [ ] Start/Stop Button
- [ ] Strategy Selector
- [ ] Trade History Table
- [ ] Profit/Loss Display
- [ ] Settings Panel
- [ ] Notification Toast
- [ ] Loading States
- [ ] Error States

### 7. Screens cần thiết

#### 7.1 Dashboard (Màn hình chính)
- Chart view (TradingView style)
- Price ticker
- Balance overview
- Quick stats (PnL, Win rate, Total trades)

#### 7.2 Trading Control
- Start/Stop bot
- Strategy selection (SMA Crossover)
- Risk management settings
- Trading status indicator

#### 7.3 Trade History
- Order history table
- Filters (Date, Type, Status)
- Export functionality

#### 7.4 Settings
- API Configuration
- Bot parameters
- Notification settings
- Theme settings

### 8. Responsive Design

**Breakpoints:**
- Mobile: 320px - 767px
- Tablet: 768px - 1023px
- Desktop: 1024px+

**Priority:** Desktop-first (Trading platform thường dùng trên desktop)

### 9. Export History

| Version | Date | Description | Designer |
|---------|------|-------------|----------|
| v1.0 | 2025-10-28 | Initial design | [Tên] |
| | | | |

### 10. Resources & Inspiration

**Tham khảo:**
- Binance Trading UI
- TradingView Charts
- Coinbase Pro Interface
- Bybit Trading Platform

**Figma Plugins hữu ích:**
- Iconify (Icons)
- Chart (Tạo charts)
- Content Reel (Mock data)
- Contrast (Kiểm tra accessibility)

### 11. Collaboration

**Review Process:**
1. Designer tạo design → Tag reviewer trên Figma
2. Team review và comment trên Figma
3. Designer update theo feedback
4. Approve → Export → Push lên GitHub

**Communication:**
- Sử dụng comments trên Figma
- Update status trên GitHub Issues
- Weekly design review meeting

---

## 📝 Notes

- Luôn backup file .fig trước khi thay đổi lớn
- Sử dụng version control trên Figma
- Document tất cả các quyết định design
- Sync với developers trước khi finalize

## 🔗 Quick Links

### 📚 Documentation
- 🎯 **[Cách Xem Design](./HOW_TO_VIEW_DESIGN.md)** ⭐ - Hướng dẫn xem và kiểm tra design Figma
- 📋 **[Review Checklist](./REVIEW_CHECKLIST.md)** - Checklist đầy đủ để review design
- 🚀 **[Quick Start](./QUICK_START.md)** - Bắt đầu nhanh cho designer và developer
- 📐 **[Wireframes](./wireframes.md)** - Wireframe và specs chi tiết
- 📅 **[Changelog](./CHANGELOG.md)** - Lịch sử thay đổi design

### 🎨 Design Resources
- [Figma Project](#) - Link Figma chính (cập nhật sau)
- [Design Tokens JSON](./design-tokens.json) - Colors, spacing, typography
- [Design Tokens CSS](./tokens.css) - CSS variables
- [Design Tokens TypeScript](./tokens.ts) - TypeScript constants

### 📁 Folders
- [Figma Files](./figma-files/) - File .fig exports
- [Screenshots](./screenshots/) - Preview images
- [Assets](./assets/) - Icons, images, components

---

## ❓ Câu Hỏi Thường Gặp

### Làm sao để xem design?
👉 Đọc: **[HOW_TO_VIEW_DESIGN.md](./HOW_TO_VIEW_DESIGN.md)**

Tóm tắt:
1. Mở link Figma trong `figma-files/README.md` (nhanh nhất)
2. Hoặc import file .fig vào Figma
3. Hoặc xem screenshots trong folder `screenshots/`

### Làm sao để inspect design (lấy specs)?
👉 Đọc: [HOW_TO_VIEW_DESIGN.md - Section Inspect](./HOW_TO_VIEW_DESIGN.md#-cách-inspect-design-cho-developers)

1. Click vào element trong Figma
2. Panel bên phải sẽ hiện specs (size, color, font, spacing)
3. Tab "Code" để copy CSS

### Làm sao để review design?
👉 Đọc: **[REVIEW_CHECKLIST.md](./REVIEW_CHECKLIST.md)**

1. Mở Figma design
2. Follow checklist trong file trên
3. Comment trực tiếp trên Figma

### Làm sao để sử dụng design tokens trong code?
```typescript
// Import TypeScript tokens
import { tokens } from './design/tokens';

const style = {
  color: tokens.colors.primary,
  fontSize: tokens.typography.fontSize.base,
  padding: tokens.spacing.md,
};
```

```css
/* Import CSS variables */
@import './design/tokens.css';

.button {
  background: var(--color-primary);
  font-size: var(--font-size-base);
  padding: var(--spacing-md);
}
```

### Làm sao để export design từ Figma?
👉 Đọc: [QUICK_START.md - Export & Push](./QUICK_START.md)

1. File → Save as .fig
2. Export screenshots (PNG)
3. Save vào folders tương ứng
4. Commit lên GitHub

---

## 🎓 Learning Resources

- [Figma for Developers](https://www.figma.com/resources/learn-design/developers/)
- [How to Inspect Designs in Figma](https://help.figma.com/hc/en-us/articles/360055203533)
- [Design Tokens Overview](https://www.youtube.com/watch?v=wtTstdiBuUk)

---

**Need help? Check [HOW_TO_VIEW_DESIGN.md](./HOW_TO_VIEW_DESIGN.md) hoặc tạo GitHub Issue với label `design`!**
