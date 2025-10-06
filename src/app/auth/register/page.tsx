"use client";
import Header from "@/components/Header";
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

export default function SignUpForm() {
  const [generalError, setGeneralError] = useState<string | null>(null);

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

  return (
    <>
      <Header></Header>
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
          <form>
            <Flex
              gap="sm"
              justify="center"
              align="center"
              direction="column"
              wrap="wrap"
            >
              <Title order={2} mb="xl">
                Реєстрація
              </Title>

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

              <PasswordInput
                w="100%"
                label="Підтвердіть пароль"
                placeholder="Підтвердіть пароль"
                {...form.getInputProps("confirmPassword")}
              />
              {generalError && (
                <Text c="red" size="sm" mt="xs">
                  {generalError}
                </Text>
              )}

              <Button w="100%" type="submit" mt="md" radius="xl" color="black">
                ЗАРЕЄСТРУВАТИСЯ
              </Button>

              <Text mt="md" size="sm">
                Або увійдіть за допомогою:
              </Text>
              <Link href="/auth/login">
                <Text c="black" fw={500} style={{ cursor: "pointer" }}>
                  УВІЙТИ
                </Text>
              </Link>
            </Flex>
          </form>
        </Box>
      </Center>
    </>
  );
}
