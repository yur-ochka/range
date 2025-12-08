export interface Category {
    id: string;
    title: string;
    description: string;
    image_url: string | null;
    alt_text: string | null;
    created_at: string;
    products_count: number;
}

export interface Product {
    id: string;
    title: string;
    description: string;
    brand: string;
    price: string;
    image_url: string;
    alt_text: string | null;
    in_stock: boolean;
    rating: number;
    category_id: string;
}
