"use client";
import { api } from "@/lib/api";
import {
  Box,
  Group,
  Image,
  Stack,
  Title,
  Text,
  Rating,
  Button,
  Center,
  Flex,
} from "@mantine/core";
import { use, useEffect, useState } from "react";

export interface ItemProps {
  id: string;
  title: string;
  subtitile: string | null;
  description: string | null;
  inStock?: boolean;
  price: number;
  image_url: string | null;
  altText?: string;
  rating?: number;
  createdAt: string;
  updatedAt: string;
}
export default function ItemPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const [product, setProduct] = useState<ItemProps | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function addToCart(productId: string, quantity: number = 1) {
    try {
      await api("/api/cart/items/", {
        method: "POST",
        body: JSON.stringify({ product_id: productId, quantity }),
      });
      alert("Товар додано до кошика!");
    } catch (err) {
      console.error(err);
      alert("Помилка при додаванні товару в кошик");
    }
  }

  useEffect(() => {
    const loadProduct = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(
          `https://range-lvzt.onrender.com/api/catalog/products/${id}/`
        );
        if (!res.ok) throw new Error("Failed to fetch product");
        const data: ItemProps = await res.json();
        setProduct(data);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    loadProduct();
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!product) return <div>No category found</div>;

  return (
    <Center py="xl">
      <Box w="90%" maw={1200}>
        <Group align="flex-start" wrap="nowrap">
          <Image
            src={product.image_url}
            alt={product.altText ?? ""}
            fit="contain"
            mah={600}
            maw={500}
            style={{ flexShrink: 0 }}
          />

          <Stack h={600} justify="space-between" p="lg" style={{ flex: 1 }}>
            <Stack gap="md">
              <Title order={1} style={{ lineHeight: 1.15 }}>
                {product.title}
              </Title>

              <Text c={product.inStock ? "green" : "red"}>
                {product.inStock ? "В наявності" : "Немає в наявності"}
              </Text>

              <Title order={2}>{product.price} грн</Title>

              <div>
                <Text fw={600} mb={4}>
                  Рейтинг товару:
                </Text>
                <Rating
                  value={product.rating}
                  fractions={10}
                  readOnly
                  size="lg"
                  color="orange"
                />
              </div>
            </Stack>

            <Stack gap="md">
              <Group gap="md">
                <Button
                  onClick={() => addToCart(product.id)}
                  variant="filled"
                  color="black"
                  radius="md"
                >
                  Додати до кошика
                </Button>
                <Button variant="outline" color="dark" radius="md">
                  Оформити замовлення
                </Button>
              </Group>
            </Stack>
          </Stack>
        </Group>
      </Box>
    </Center>
  );
}
