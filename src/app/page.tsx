import Image from "next/image";
import { Button } from "@mantine/core";

export default function Home() {
  return (
    <div>
      <h1 className="text-2xl font-bold underline">Hello world!</h1>
      <Button w="100%" type="submit" mt="md" radius="xl" color="cyan">
        LOGIN
      </Button>
    </div>
  );
}
