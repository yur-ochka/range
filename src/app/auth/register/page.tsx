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
import { useForm, matchesField, isEmail, hasLength } from "@mantine/form";
import Link from "next/link";
import { useState } from "react";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function SignUpForm() {
  const [generalError, setGeneralError] = useState<string | null>(null);
  const router = useRouter();

  const form = useForm({
    mode: "uncontrolled",
    validateInputOnBlur: true,
    initialValues: {
      email: "",
      password: "",
      confirmPassword: "",
    },
    validate: {
      email: isEmail("Некоректний email"),
      password: hasLength({ min: 8 }, "Пароль закороткий"),
      confirmPassword: matchesField("password", "Паролі не співпадають"),
    },
  });

  async function handleSubmit(e: any) {
    e.preventDefault();
    setGeneralError(null);

    if (!form.isValid()) return;

    const { email, password } = form.getValues();

    try {
      await api("/api/users/register/", {
        method: "POST",
        body: JSON.stringify({
          email: email,
          username: email,
          first_name: "Place",
          last_name: "Place",
          password: password,
          password_confirm: form.getValues().confirmPassword,
        }),
      });

      router.push("/auth/login");
      localStorage.setItem("username", email);
    } catch (err: any) {
      setGeneralError(err.message);
    }
  }

  return (
    <Center h="80vh" w="100vw" p="md">
      <Box
        style={{
          width: "100%",
          maxWidth: 400,
          backgroundColor: "#F5F5F5",
          borderRadius: "18px",
          padding: "2rem",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
        }}
      >
        <form onSubmit={handleSubmit}>
          <Flex gap="sm" direction="column" align="center">
            <Title order={2}>Реєстрація</Title>

            <TextInput
              w="100%"
              label="Логін"
              {...form.getInputProps("email")}
            />

            <PasswordInput
              w="100%"
              label="Пароль"
              {...form.getInputProps("password")}
            />

            <PasswordInput
              w="100%"
              label="Підтвердіть пароль"
              {...form.getInputProps("confirmPassword")}
            />

            {generalError && (
              <Text c="red" size="sm">
                {generalError}
              </Text>
            )}

            <Button w="100%" type="submit" radius="xl" color="black">
              ЗАРЕЄСТРУВАТИСЯ
            </Button>

            <Text size="sm">Або увійдіть:</Text>
            <Link href="/auth/login">
              <Text c="black" fw={500}>
                УВІЙТИ
              </Text>
            </Link>
          </Flex>
        </form>
      </Box>
    </Center>
  );
}
