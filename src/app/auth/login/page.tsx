"use client";

import {
  Button,
  TextInput,
  Title,
  PasswordInput,
  Flex,
  Center,
  Box,
  Text,
} from "@mantine/core";
import { useForm, isEmail, hasLength } from "@mantine/form";
import Link from "next/link";
import { useState } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function LoginForm() {
  const [generalError, setGeneralError] = useState<string | null>(null);
  const router = useRouter();

  const form = useForm({
    mode: "uncontrolled",
    validateInputOnBlur: true,
    initialValues: {
      email: "",
      password: "",
    },
    validate: {
      email: isEmail("Некоректний email"),
      password: hasLength({ min: 8 }, "Пароль закороткий"),
    },
  });

  async function handleSubmit(e: any) {
    e.preventDefault();
    setGeneralError(null);

    if (!form.isValid()) return;

    const { email, password } = form.getValues();

    try {
      const res = await api("/api/users/login/", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      sessionStorage.setItem("access", res.access);
      localStorage.setItem("refresh", res.refresh);

      router.push("/");
      localStorage.setItem("username", email);
    } catch (err: any) {
      setGeneralError(err.message);
    }
  }

  return (
    <Center h="80vh" w="100vw">
      <Box
        style={{
          width: "90%",
          maxWidth: 400,
          backgroundColor: "#F5F5F5",
          padding: "2rem",
          borderRadius: "8px",
          boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
        }}
      >
        <form onSubmit={handleSubmit}>
          <Flex gap="sm" direction="column" align="center">
            <Title order={2}>Увійти</Title>

            <TextInput
              w="100%"
              label="Логін"
              placeholder="your@email.com"
              {...form.getInputProps("email")}
            />

            <PasswordInput
              w="100%"
              label="Пароль"
              placeholder="Введіть пароль"
              {...form.getInputProps("password")}
            />

            {generalError && (
              <Text c="red" size="sm">
                {generalError}
              </Text>
            )}

            <Button w="100%" type="submit" color="black" radius="xl">
              УВІЙТИ
            </Button>

            <Text size="sm">Або зареєструйтесь:</Text>
            <Link href="/auth/register">
              <Text c="black" fw={500}>
                РЕЄСТРАЦІЯ
              </Text>
            </Link>
          </Flex>
        </form>
      </Box>
    </Center>
  );
}
