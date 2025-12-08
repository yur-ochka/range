export async function getCategories() {
    const res = await fetch("https://range-lvzt.onrender.com/api/catalog/categories/", {
        next: { revalidate: 60 }, // кеш 1 хвилина
    });

    if (!res.ok) {
        throw new Error("Failed to fetch categories");
    }

    return res.json();
}
