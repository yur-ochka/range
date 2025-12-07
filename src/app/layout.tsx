import "@mantine/core/styles.css";
import "./globals.css";
import { MantineProvider } from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import "@mantine/notifications/styles.css";
import "@mantine/dates/styles.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { AuthProvider } from "@/context/AuthContext";

export const metadata = {
  title: "Range",
  description: "Your best shopping companion",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" data-mantine-color-scheme="light">
      <body>
        <AuthProvider>
          {" "}
          <MantineProvider
            theme={{
              fontFamily: '"Comic Sans MS", cursive, sans-serif',
            }}
          >
            <Notifications />
            <Header></Header>
            {children}
            <Footer></Footer>
          </MantineProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
