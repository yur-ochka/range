"use client";
import { CategoryList } from "@/components/main";
import { Button, Image, Title, Box, Center } from "@mantine/core";
import { useEffect, useState } from "react";
import { CategoryCardProps } from "@/components/main";

export default function Home() {
  const [categories, setCategories] = useState<CategoryCardProps[]>([]);
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const res = await fetch(
          "https://range-lvzt.onrender.com/api/catalog/categories/"
        );
        const data = await res.json();

        setCategories(data.results);
      } catch (err) {
        console.error(err);
      }
    };

    loadCategories();
  }, []);

  return (
    <>
      <Box px="67px">
        <Image src="/mainPagePic.png" alt="super kartinka" w="100%" pb={"xl"} />
        <Title order={1} pb={"xl"}>
          Каталог товарів
        </Title>
        <CategoryList categories={categories}></CategoryList>
        <Center pb="xl">
          <Button radius="xl" color="black" variant="filled" size="lg">
            Завантажити ще
          </Button>
        </Center>
      </Box>
    </>
  );
}
