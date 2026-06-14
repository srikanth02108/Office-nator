'use client'

import Link from 'next/link'
import { AtSign, Bot, Code2, Share2 } from 'lucide-react'

const COLUMNS = [
  {
    title: 'Product',
    links: ['Features', 'Architecture', 'Roadmap', 'Pricing', 'Demo'],
  },
  {
    title: 'Developer',
    links: ['GitHub', 'Docs', 'API Reference', 'Changelog'],
  },
  {
    title: 'Company',
    links: ['About', 'Blog', 'Careers', 'Contact', 'Privacy', 'Terms'],
  },
]

export function SiteFooter() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 gap-10 md:grid-cols-4">
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center gap-2.5">
              <span className="flex size-9 items-center justify-center rounded-md border border-primary/40 bg-primary/10 text-primary">
                <Bot className="size-5" />
              </span>
              <span className="text-sm font-bold tracking-tight">
                OFFICE-NATOR
              </span>
            </Link>
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-muted-foreground">
              Voice-controlled AI desktop automation. Speak in your language,
              and watch your office tools obey.
            </p>
            <div className="mt-5 flex gap-3">
              {[Code2, AtSign, Share2].map((Icon, i) => (
                <a
                  key={i}
                  href="https://github.com"
                  target="_blank"
                  rel="noreferrer noopener"
                  aria-label="Social link"
                  className="flex size-9 items-center justify-center rounded-md border border-border text-muted-foreground transition-colors hover:text-foreground"
                >
                  <Icon className="size-4" />
                </a>
              ))}
            </div>
          </div>

          {COLUMNS.map((col) => (
            <div key={col.title}>
              <h3 className="font-mono text-xs uppercase tracking-[0.2em] text-foreground">
                {col.title}
              </h3>
              <ul className="mt-4 flex flex-col gap-2.5">
                {col.links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-3 border-t border-border pt-6 text-sm text-muted-foreground sm:flex-row">
          <span>© 2026 OFFICE-NATOR · Built for Bharat · MIT License</span>
          <span className="font-mono text-xs">Made with voice</span>
        </div>
      </div>
    </footer>
  )
}
