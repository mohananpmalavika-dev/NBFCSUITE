import './globals.css';

export const metadata = {
  title: 'ARTH.OS Enterprise Shell',
  description: 'ARTH.OS enterprise design system shell implementation',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
