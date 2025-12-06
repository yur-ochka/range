"use client";
import { Box, Title } from "@mantine/core";
import { use, useEffect, useState } from "react";
import { ItemList } from "@/components/category";
import { CategoryCardProps } from "@/components/main";

export default function CategoryPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const [category, setCategory] = useState<CategoryCardProps | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadCategory = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(
          `https://range-lvzt.onrender.com/api/catalog/categories/${id}/`
        );
        if (!res.ok) throw new Error("Failed to fetch category");
        const data: CategoryCardProps = await res.json();
        setCategory(data);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    loadCategory();
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!category) return <div>No category found</div>;

  return (
    <Box px="67px">
      <Title order={1} pb="xl">
        {category.title}
      </Title>
      {category.products && <ItemList items={category.products} />}
    </Box>
  );
}
