import type { InputHTMLAttributes, LabelHTMLAttributes, ReactNode, ButtonHTMLAttributes } from "react";
import { forwardRef } from "react";

export function Field({
  label,
  hint,
  children,
  ...props
}: { label: string; hint?: string; children: ReactNode } & LabelHTMLAttributes<HTMLLabelElement>) {
  return (
    <label className="flex flex-col gap-1.5 text-sm" {...props}>
      <span className="font-medium text-foreground">{label}</span>
      {children}
      {hint && <span className="text-xs text-muted-foreground">{hint}</span>}
    </label>
  );
}

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  function Input(props, ref) {
    return (
      <input
        ref={ref}
        {...props}
        className={`field focus:field-focus ${props.className ?? ""}`}
      />
    );
  },
);

type BtnProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "outline" | "ghost" | "destructive";
};
export const Button = forwardRef<HTMLButtonElement, BtnProps>(function Button(
  { variant = "primary", className, ...rest },
  ref,
) {
  const cls =
    variant === "primary"
      ? "btn btn-primary hover:btn-primary-hover"
      : variant === "outline"
        ? "btn btn-outline hover:bg-secondary"
        : variant === "destructive"
          ? "btn bg-destructive text-destructive-foreground hover:opacity-90"
          : "btn btn-ghost hover:bg-secondary";
  return (
    <button
      ref={ref}
      {...rest}
      className={`${cls} disabled:opacity-50 disabled:cursor-not-allowed ${className ?? ""}`}
    />
  );
});

export function Card({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={`card-surface p-6 ${className}`}>{children}</div>;
}

export function StatCard({
  label,
  value,
  hint,
  icon,
}: {
  label: string;
  value: ReactNode;
  hint?: string;
  icon?: ReactNode;
}) {
  return (
    <div className="card-surface p-5">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground">{label}</div>
          <div className="mt-1 font-display text-3xl">{value}</div>
          {hint && <div className="mt-1 text-xs text-muted-foreground">{hint}</div>}
        </div>
        {icon && (
          <div className="rounded-lg bg-secondary p-2 text-secondary-foreground">{icon}</div>
        )}
      </div>
    </div>
  );
}

export function Alert({
  tone = "info",
  children,
}: {
  tone?: "info" | "error" | "success";
  children: ReactNode;
}) {
  const cls =
    tone === "error"
      ? "border-destructive/40 bg-destructive/10 text-destructive"
      : tone === "success"
        ? "border-brand/30 bg-brand/10 text-brand"
        : "border-border bg-muted text-muted-foreground";
  return (
    <div className={`rounded-md border px-3 py-2 text-sm ${cls}`}>{children}</div>
  );
}
