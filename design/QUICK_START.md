# Quick Start Guide - Design với Figma

## 🚀 Bắt đầu nhanh (10 phút)

### Bước 1: Tạo Figma Project
1. Đăng nhập Figma (figma.com)
2. Tạo project mới: "Crypto Trading Bot"
3. Mời team members
4. Copy link project vào `design/README.md`

### Bước 2: Import Design System
1. Tạo page "Design System"
2. Import colors từ `design-tokens.json`
3. Tạo color styles:
   - Primary/Main: `#F0B90B`
   - Success: `#0ECB81`
   - Danger: `#F6465D`
   - Background: `#0B0E11`
   - Text/Primary: `#EAECEF`

4. Tạo text styles:
   - H1: Inter, Bold, 32px
   - H2: Inter, Semibold, 24px
   - Body: Inter, Regular, 16px
   - Caption: Inter, Regular, 14px

### Bước 3: Tạo Components
Theo thứ tự ưu tiên:

1. **Buttons** (20 phút)
   - Primary button (Green)
   - Danger button (Red)
   - Secondary button
   - States: Default, Hover, Active, Disabled

2. **Input Fields** (15 phút)
   - Text input
   - Dropdown
   - Slider
   - States: Default, Focus, Error

3. **Cards** (10 phút)
   - Default card container
   - Stat card (Balance, PnL)
   - Trading card

4. **Status Indicators** (5 phút)
   - Active dot (Green)
   - Stopped dot (Red)
   - Paused dot (Yellow)

### Bước 4: Tạo Screens (Theo wireframe)

#### Screen 1: Dashboard (45 phút)
- [ ] Header với logo và navigation
- [ ] Chart container (placeholder)
- [ ] Control panel sidebar
- [ ] Stats cards
- [ ] Recent trades table

#### Screen 2: Trading Control (30 phút)
- [ ] Strategy configuration form
- [ ] Risk management settings
- [ ] Trading log/console

#### Screen 3: Trade History (20 phút)
- [ ] Filters bar
- [ ] Table với pagination
- [ ] Summary statistics

#### Screen 4: Settings (20 phút)
- [ ] Tabs navigation
- [ ] API configuration form
- [ ] Bot settings form

### Bước 5: Export & Push
```bash
# Export file Figma
File → Save as .fig → Lưu vào design/figma-files/

# Export screenshots
Select frame → Export → PNG → 2x → Lưu vào design/screenshots/

# Commit lên GitHub
cd F:\CNPM\Project
git add design/
git commit -m "design: add initial screens v1.0"
git push origin main
```

---

## 📋 Design Checklist

### Pre-Design
- [ ] Đọc requirements trong README.md
- [ ] Review wireframes.md
- [ ] Setup Figma project
- [ ] Import design tokens
- [ ] Create component library

### Design Phase
- [ ] Create design system page
- [ ] Build reusable components
- [ ] Design all 4 main screens
- [ ] Add interactive prototype
- [ ] Test responsive layouts
- [ ] Add annotations/notes

### Review Phase
- [ ] Self-review completeness
- [ ] Check color contrast (accessibility)
- [ ] Verify all states (hover, active, disabled)
- [ ] Test prototype flow
- [ ] Get team feedback
- [ ] Iterate based on feedback

### Export & Delivery
- [ ] Export .fig file
- [ ] Export screenshots (all screens)
- [ ] Export assets (icons, logos)
- [ ] Update CHANGELOG.md
- [ ] Update version history table
- [ ] Commit to GitHub
- [ ] Notify developers

---

## 🎨 Tips & Best Practices

### Figma Organization
```
📁 Crypto Trading Bot
  📄 Cover (Project info)
  📄 Design System
    - Colors
    - Typography
    - Spacing
    - Components
  📄 Screens - Desktop
    - Dashboard
    - Trading Control
    - History
    - Settings
  📄 Screens - Mobile (Optional)
  📄 Prototypes
  📄 Archive (Old versions)
```

### Component Naming
- Use clear, descriptive names
- Format: `Category/Name/Variant`
- Example: `Button/Primary/Default`
- Example: `Card/Stat/Balance`

### Auto Layout
- Use auto-layout for all components
- Set proper padding and spacing
- Makes responsive design easier
- Faster iterations

### Color Management
- Use styles, not raw hex values
- Name colors semantically: `success`, `danger`, not `green`, `red`
- Create dark mode variants if needed

### Typography
- Use text styles consistently
- Don't manually adjust size/weight
- Create styles for all text types

---

## 🔗 Resources

### Figma Plugins (Must-have)
1. **Iconify** - 100k+ icons
2. **Unsplash** - Free images
3. **Content Reel** - Generate fake data
4. **Contrast** - Check accessibility
5. **Chart** - Create data visualizations

### Reference Designs
- [Binance UI](https://www.binance.com/en/trade/BTC_USDT)
- [TradingView](https://www.tradingview.com/)
- [Coinbase Pro](https://pro.coinbase.com/)

### Design Inspiration
- [Dribbble: Crypto Dashboard](https://dribbble.com/search/crypto-dashboard)
- [Behance: Trading UI](https://www.behance.net/search/projects?search=trading+ui)

### Learn Figma
- [Figma Official Tutorials](https://www.youtube.com/c/Figma)
- [Figma Best Practices](https://www.figma.com/best-practices/)

---

## ⚠️ Common Mistakes to Avoid

1. ❌ Không sử dụng components → Khó maintain
   ✅ Tạo components cho mọi element tái sử dụng

2. ❌ Hard-code colors → Inconsistent
   ✅ Dùng color styles từ design system

3. ❌ Không đặt tên layer → Confusing
   ✅ Đặt tên rõ ràng cho mọi layer

4. ❌ Quên export assets → Developers không có resources
   ✅ Export SVG cho icons, PNG cho images

5. ❌ Không test prototype → Broken flow
   ✅ Test flow trước khi handoff

6. ❌ Không document → Developers confused
   ✅ Add notes và annotations

---

## 📞 Support

Nếu cần hỗ trợ:
1. Check `design/README.md` cho guidelines
2. Check `design/wireframes.md` cho specs
3. Hỏi trong team chat
4. Tag reviewer trên Figma comments

---

## 🎯 Next Steps

Sau khi hoàn thành design:
1. ✅ Export all files
2. ✅ Push to GitHub
3. ✅ Create handoff document
4. ✅ Schedule review meeting
5. ✅ Support developers during implementation

---

**Time estimate:**
- Setup: 30 minutes
- Components: 1-2 hours
- Screens: 3-4 hours
- Review & iterate: 1-2 hours
- **Total: 6-9 hours** for complete design
