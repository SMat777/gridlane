"use client";

/**
 * Inline field error display for config forms.
 *
 * Shows a red error message below a form field when validation fails.
 * Returns null when there's no error — zero visual impact on valid fields.
 */

interface FieldErrorProps {
  errors?: Record<string, string>;
  field: string;
}

export function FieldError({ errors, field }: FieldErrorProps) {
  const message = errors?.[field];
  if (!message) return null;

  return (
    <p className="text-xs text-red-600 dark:text-red-400" role="alert">
      {message}
    </p>
  );
}

/**
 * Helper to add error styling to input borders.
 * Returns a className string: red border if field has error, empty otherwise.
 */
export function fieldErrorClass(
  errors: Record<string, string> | undefined,
  field: string,
): string {
  return errors?.[field]
    ? "border-red-500 dark:border-red-400 focus-visible:ring-red-500"
    : "";
}
