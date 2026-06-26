export const metadata = {
  title: 'NBFCSUITE Customer Portal',
  description: 'Loan management and financial services portal',
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
