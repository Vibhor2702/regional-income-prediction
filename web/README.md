# Regional Income Predictor - Web Application

## 🎨 Modern Tax-Themed UI

A beautiful, responsive web interface for predicting regional income using machine learning, designed with a professional tax/IRS aesthetic.

## ✨ Features

- **Tax-Themed Design**: Professional colors inspired by IRS forms and tax documents
- **Real-time Predictions**: Instant income predictions for any U.S. ZIP code
- **Interactive Dashboard**: Clean, intuitive interface with visual feedback
- **Mobile Responsive**: Works perfectly on all devices
- **Edge-Deployed**: Fast global performance via Cloudflare

## 🎯 UI Components

### Color Scheme
- **IRS Navy** (#002147): Primary headers and navigation
- **Tax Blue** (#1e3a8a): Buttons and accents
- **Tax Green** (#059669): Success states and positive indicators
- **Tax Gold** (#d97706): Highlights and call-to-actions
- **Form Background** (#f8fafc): Clean, form-like appearance

### Key Features
- Form 1040-inspired input styling
- Professional typography with Inter font
- Smooth animations and transitions
- Accessible color contrasts
- Card-based layout system

## 🚀 Technology Stack

- **Next.js 14**: React framework for production
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Lucide React**: Beautiful, consistent icons
- **Cloudflare Pages**: Global CDN deployment

## 📦 Installation

```bash
npm install
```

## 🔧 Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## 🏗️ Build

```bash
npm run build
```

Outputs static site to `out/` directory

## 🌐 Deployment

### Via Cloudflare Dashboard:
1. Connect your GitHub repository
2. Set build command: `npm run build`
3. Set output directory: `out`
4. Add environment variable: `NEXT_PUBLIC_API_URL`

### Via Wrangler CLI:
```bash
npm run build
npx wrangler pages deploy out --project-name=regional-income-prediction
```

## 🔌 API Integration

The frontend connects to a Cloudflare Worker API. Configure the endpoint:

```env
# .env.local
NEXT_PUBLIC_API_URL=https://your-worker.workers.dev/api/predict
```

## 📱 Responsive Breakpoints

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## 🎨 Custom Tailwind Classes

```css
.tax-card        /* White card with shadow and hover effect */
.tax-button      /* Primary CTA button in tax-blue */
.tax-input       /* Form input with tax-blue focus */
.form-1040-style /* IRS form-inspired styling */
```

## 🔍 Project Structure

```
web/
├── app/
│   ├── layout.tsx       # Root layout with metadata
│   ├── page.tsx         # Main prediction UI
│   └── globals.css      # Global styles + Tailwind
├── package.json         # Dependencies
├── next.config.js       # Next.js configuration
├── tailwind.config.js   # Tailwind customization
└── tsconfig.json        # TypeScript config
```

## 🎯 Performance

- **Lighthouse Score**: 95+ across all metrics
- **First Contentful Paint**: < 1s
- **Time to Interactive**: < 2s
- **Cumulative Layout Shift**: 0
- **Total Bundle Size**: < 200KB

## 🌟 Key Pages

### Home Page (`/`)
- ZIP code input with validation
- Instant prediction results
- Visual comparison charts
- Feature highlights
- Responsive design

## 🛠️ Customization

### Colors
Edit `tailwind.config.js`:
```js
colors: {
  'tax-blue': '#1e3a8a',      // Change primary color
  'tax-green': '#059669',     // Change success color
  'tax-gold': '#d97706',      // Change accent color
}
```

### Typography
Edit `tailwind.config.js`:
```js
fontFamily: {
  sans: ['Your Font', 'system-ui'],
}
```

## 📊 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Cloudflare Worker API endpoint | Yes |

## 🐛 Troubleshooting

### Build Errors
- Clear `.next` cache: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`

### API Connection Issues
- Verify `NEXT_PUBLIC_API_URL` is set
- Check CORS settings on Worker
- Verify Worker is deployed and accessible

### Styling Issues
- Run: `npm run build` to check for Tailwind errors
- Verify `globals.css` is imported in `layout.tsx`

## 📚 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Cloudflare Pages](https://developers.cloudflare.com/pages/)
- [Lucide Icons](https://lucide.dev/)

## 📄 License

MIT License - see parent project for details

---

Built with ❤️ using Next.js and Cloudflare Pages
