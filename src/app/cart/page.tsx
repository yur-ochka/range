"use client";

import { useEffect, useState } from "react";
import {
  Button,
  Text,
  NumberInput,
  Flex,
  Box,
  Loader,
  Center,
} from "@mantine/core";
import { api } from "@/lib/api";

interface CartItem {
  id: string;
  product_title: string;
  unit_price: number;
  quantity: number;
}

export default function CartPage() {
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);

  // --------------------------
  // Завантаження кошика
  // --------------------------
  async function loadCart() {
    setLoading(true);
    try {
      const data = await api("/api/cart/");
      console.log(data);
      setCartItems(data.items); // припускаємо, що бекенд повертає {items: [...]}
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCart();
  }, []);

  // --------------------------
  // Змінити кількість / видалити
  // --------------------------
  async function updateItem(itemId: string, quantity: number) {
    try {
      if (quantity <= 0) {
        await api(`/api/cart/items/${itemId}/`, {
          method: "DELETE",
        });
      } else {
        await api(`/api/cart/items/${itemId}/`, {
          method: "PATCH",
          body: JSON.stringify({ quantity }),
        });
      }
      await loadCart();
    } catch (err) {
      console.error(err);
    }
  }

  if (loading) return <Loader />;

  if (cartItems.length === 0)
    return (
      <Center>
        <Text>Ваш кошик порожній 🛒</Text>
      </Center>
    );

  return (
    <Box p="md">
      <Text size="xl" mb="md">
        Ваш кошик 🛒
      </Text>
      {cartItems.map((item) => (
        <Flex
          key={item.id}
          align="center"
          justify="space-between"
          mb="sm"
          p="sm"
          style={{ border: "1px solid #ddd", borderRadius: 8 }}
        >
          <Text>{item.product_title}</Text>
          <Text>{item.unit_price * item.quantity} ₴</Text>
          <Flex align="center" gap="xs">
            <Button
              size="xs"
              onClick={() => updateItem(item.id, item.quantity - 1)}
            >
              -
            </Button>
            <NumberInput
              value={item.quantity}
              onChange={(val) => updateItem(item.id, Number(val) || 1)}
              min={1}
              max={999}
              style={{ width: 60 }}
            />
            <Button
              size="xs"
              onClick={() => updateItem(item.id, item.quantity + 1)}
            >
              +
            </Button>
            <Button
              color="red"
              size="xs"
              onClick={() => updateItem(item.id, 0)}
            >
              Видалити
            </Button>
          </Flex>
        </Flex>
      ))}
    </Box>
  );
}
