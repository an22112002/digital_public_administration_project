export interface Service {
    id: string
    name: string
    description: string
    category: ServiceCategory
}

export type ServiceCategory = 'Chứng thực' | 'Hộ tịch' | 'Hộ kinh doanh' | 'An toàn thực phẩm'