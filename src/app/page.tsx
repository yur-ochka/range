export const mockCategories = [
  {
    id: "1",
    title: "Фронтенд розробка",
    description:
      "Вивчення React, Next.js, TailwindCSS та сучасних технологій фронтенду.",
    imageUrl: "https://picsum.photos/seed/frontend/400/300",
    altText: "Frontend development illustration",
  },
  {
    id: "2",
    title: "Бекенд розробка",
    description: "Основи Node.js, Express, баз даних і REST API.",
    imageUrl: "https://picsum.photos/seed/backend/400/300",
    altText: "Backend development illustration",
  },
  {
    id: "3",
    title: "Дизайн UI/UX",
    description:
      "Основи створення інтерфейсів, фреймворки дизайну, користувацький досвід.",
    imageUrl: "https://picsum.photos/seed/design/400/300",
    altText: "UI/UX design example",
  },
  {
    id: "4",
    title: "Мобільна розробка",
    description:
      "Створення застосунків для Android та iOS з використанням React Native.",
    imageUrl: "https://picsum.photos/seed/mobile/400/300",
    altText: "Mobile app development",
  },
  {
    id: "5",
    title: "Штучний інтелект",
    description: null,
    imageUrl: "https://picsum.photos/seed/ai/400/300",
    altText: "Artificial intelligence concept",
  },
];

import Header from "@/components/Header";
import { CategoryList } from "@/components/main";
import { Button, Image, Title, Box, Center } from "@mantine/core";
export default function Home() {
  return (
    <>
      <Header></Header>
      <Box px="67px">
        <Image src="/mainPagePic.png" alt="super kartinka" w="100%" pb={"xl"} />
        <Title order={1} pb={"xl"}>
          Каталог товарів
        </Title>
        <CategoryList categories={mockCategories}></CategoryList>
        <Center pb="xl">
          <Button radius="xl" color="black" variant="filled" size="lg">
            Завантажити ще
          </Button>
        </Center>
      </Box>
    </>
  );
}
