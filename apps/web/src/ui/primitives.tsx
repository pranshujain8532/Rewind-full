// Adapted from shadcn/ui at 30a58d4498f270af1c1e981a7d78a15cf5740841 (MIT).
// Full licence: public/licenses/shadcn-MIT.txt. Provenance: COMPONENT-SOURCES.md.
// Tailwind/cn/cva replaced with REWIND CSS; title slots use semantic headings.
import type { ComponentProps } from 'react';

export function Card({ className = '', ...props }: ComponentProps<'div'>) {
  return <div data-slot="card" className={`panel ${className}`} {...props} />;
}
export function CardHeader({ className = '', ...props }: ComponentProps<'div'>) {
  return <div data-slot="card-header" className={`panel-head ${className}`} {...props} />;
}
export function CardTitle(props: ComponentProps<'h2'>) { return <h2 data-slot="card-title" {...props} />; }
export function CardDescription(props: ComponentProps<'p'>) { return <p data-slot="card-description" className="muted" {...props} />; }
export function CardContent({ className = '', ...props }: ComponentProps<'div'>) { return <div data-slot="card-content" className={`panel-body ${className}`} {...props} />; }
export function Empty({ className = '', ...props }: ComponentProps<'div'>) { return <div data-slot="empty" className={`empty-state ${className}`} {...props} />; }
export function EmptyHeader(props: ComponentProps<'div'>) { return <div data-slot="empty-header" {...props} />; }
export function EmptyTitle(props: ComponentProps<'h2'>) { return <h2 data-slot="empty-title" {...props} />; }
export function EmptyDescription(props: ComponentProps<'p'>) { return <p data-slot="empty-description" {...props} />; }
export function EmptyContent(props: ComponentProps<'div'>) { return <div data-slot="empty-content" {...props} />; }
