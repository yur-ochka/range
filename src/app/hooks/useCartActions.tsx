import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";

export function useCartActions() {
  const { user } = useAuth();
  const router = useRouter();

  async function addToCart(productId: string, quantity: number = 1) {
    if (!user) {
      alert("Щоб додати товар у кошик — увійдіть у свій акаунт!");
      router.push("/auth/login");
      return;
    }

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

  return { addToCart };
}
