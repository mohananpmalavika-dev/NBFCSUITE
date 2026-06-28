import './globals.css';

export const metadata = {
  title: 'FIN.OS Enterprise Shell',
  description: 'FIN.OS enterprise design system shell implementation',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
