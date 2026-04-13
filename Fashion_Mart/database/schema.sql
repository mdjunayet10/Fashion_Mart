-- Fashion Mart Database Schema
-- Drop database if exists and create new
DROP DATABASE IF EXISTS fashion_mart;
CREATE DATABASE fashion_mart;
USE fashion_mart;

-- Table: Admin
CREATE TABLE Admin (
    AdminID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Role VARCHAR(50) DEFAULT 'Admin',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Customer
CREATE TABLE Customer (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Number VARCHAR(15),
    RewardPoint INT DEFAULT 0,
    Road VARCHAR(100),
    Area VARCHAR(100),
    City VARCHAR(50),
    District VARCHAR(50),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Dealer
CREATE TABLE Dealer (
    DealerID INT PRIMARY KEY AUTO_INCREMENT,
    DealerName VARCHAR(100) NOT NULL,
    Contact VARCHAR(15),
    Email VARCHAR(100),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Product
CREATE TABLE Product (
    ProductID INT PRIMARY KEY AUTO_INCREMENT,
    ProductName VARCHAR(150) NOT NULL,
    Category VARCHAR(50),
    Price DECIMAL(10, 2) NOT NULL,
    Quantity INT DEFAULT 0,
    Demand INT DEFAULT 0,
    Rating DECIMAL(3, 2) DEFAULT 0.00,
    Embroidery VARCHAR(50),
    Description TEXT,
    ImageURL VARCHAR(255),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: DeliveryMan
CREATE TABLE DeliveryMan (
    DeliveryManID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Phone VARCHAR(15) NOT NULL,
    Address TEXT,
    VehicleType VARCHAR(50),
    Status VARCHAR(20) DEFAULT 'Active',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Order (Note: 'Order' is a reserved keyword, using backticks)
CREATE TABLE `Order` (
    OrderID INT PRIMARY KEY AUTO_INCREMENT,
    OrderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    TotalAmount DECIMAL(10, 2) NOT NULL,
    CustomerID INT NOT NULL,
    DeliveryManID INT,
    OrderStatus VARCHAR(20) DEFAULT 'Pending',
    PaymentMethod VARCHAR(50) DEFAULT 'Cash on Delivery',
    PaymentStatus VARCHAR(20) DEFAULT 'Pending',
    DeliveryAddress TEXT,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (DeliveryManID) REFERENCES DeliveryMan(DeliveryManID) ON DELETE SET NULL
);

-- Table: OrderItem (Junction table for Order and Product)
CREATE TABLE OrderItem (
    OrderID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (OrderID, ProductID),
    FOREIGN KEY (OrderID) REFERENCES `Order`(OrderID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID) ON DELETE CASCADE
);

-- Table: Payment
CREATE TABLE Payment (
    PaymentID INT PRIMARY KEY AUTO_INCREMENT,
    PaymentMethod VARCHAR(50) NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    PaymentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PaymentStatus VARCHAR(20) DEFAULT 'Pending',
    DealerID INT,
    OrderID INT UNIQUE NOT NULL,
    FOREIGN KEY (DealerID) REFERENCES Dealer(DealerID) ON DELETE SET NULL,
    FOREIGN KEY (OrderID) REFERENCES `Order`(OrderID) ON DELETE CASCADE
);

-- Table: Delivery
CREATE TABLE Delivery (
    DeliveryID INT PRIMARY KEY AUTO_INCREMENT,
    DeliveryDate DATE,
    DeliveryStatus VARCHAR(20) DEFAULT 'Pending',
    OrderID INT UNIQUE NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (OrderID) REFERENCES `Order`(OrderID) ON DELETE CASCADE
);

-- Table: Review
CREATE TABLE Review (
    ReviewID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT NOT NULL,
    ProductID INT NOT NULL,
    Rating INT CHECK (Rating >= 1 AND Rating <= 5),
    ReviewDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Comment TEXT,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID) ON DELETE CASCADE
);

-- Table: Ranking
CREATE TABLE Ranking (
    CustomerID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT DEFAULT 0,
    PRIMARY KEY (CustomerID, ProductID),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID) ON DELETE CASCADE
);

-- Insert sample data for testing

-- Sample Admin
INSERT INTO Admin (Username, Password, Name, Email, Role) VALUES
('admin', 'admin123', 'System Administrator', 'admin@fashionmart.com', 'Super Admin');

-- Sample Dealers
INSERT INTO Dealer (DealerName, Contact, Email) VALUES
('Fashion Hub Ltd.', '01712345678', 'fashionhub@example.com'),
('Style Point', '01823456789', 'stylepoint@example.com');

-- Sample Delivery Men
INSERT INTO DeliveryMan (Username, Password, Name, Email, Phone, Address, VehicleType, Status) VALUES
('delivery1', 'delivery123', 'Karim Rahman', 'karim@delivery.com', '01712345670', 'Mirpur, Dhaka', 'Motorcycle', 'Active'),
('delivery2', 'delivery123', 'Rahim Ahmed', 'rahim@delivery.com', '01812345671', 'Uttara, Dhaka', 'Motorcycle', 'Active'),
('delivery3', 'delivery123', 'Salam Mia', 'salam@delivery.com', '01912345672', 'Mohammadpur, Dhaka', 'Bicycle', 'Active');

-- Sample Customers
INSERT INTO Customer (Username, Password, Name, Email, Number, RewardPoint, Road, Area, City, District) VALUES
('john_doe', 'password123', 'John Doe', 'john@example.com', '01612345678', 100, 'Road 5', 'Dhanmondi', 'Dhaka', 'Dhaka'),
('jane_smith', 'password123', 'Jane Smith', 'jane@example.com', '01712345679', 50, 'Road 10', 'Gulshan', 'Dhaka', 'Dhaka'),
('guest_user', 'password123', 'Guest User', 'guest@example.com', '01812345680', 0, 'Road 1', 'Banani', 'Dhaka', 'Dhaka');

-- Sample Products
INSERT INTO Product (ProductName, Category, Price, Quantity, Embroidery, Description, ImageURL) VALUES
-- Sarees
('Elegant Silk Saree', 'Saree', 4500.00, 25, 'Hand Embroidered', 'Beautiful silk saree with traditional hand embroidery work. Perfect for weddings and special occasions.', 'https://womanhood.com.bd/cdn/shop/files/62FB7F37-D569-4B5F-8D1A-068D839DBB2A.jpg?v=1758449780&width=360'),
('Cotton Punjabi', 'Punjabi', 1800.00, 40, 'Machine Embroidered', 'Comfortable cotton punjabi for everyday wear with elegant machine embroidery.', 'https://mcprod.aarong.com/media/catalog/product/0/0/0030000140073.jpg?optimize=high&bg-color=255,255,255&fit=bounds&height=&width='),
('Designer Kurti', 'Kurti', 1200.00, 35, 'None', 'Modern designer kurti with vibrant colors and patterns.', 'https://assets0.mirraw.com/images/12379419/image_zoom.jpeg?1712410050'),
('Formal Shirt', 'Shirt', 1500.00, 50, 'None', 'Premium quality formal shirt for office and business meetings.', 'https://www.lerevecraze.com/wp-content/uploads/2025/11/ade37c2d-ee15-40d1-91ba-c4195d06b2de.jpg'),
('Embroidered Salwar Kameez', 'Salwar Kameez', 3200.00, 20, 'Hand Embroidered', 'Luxurious salwar kameez with intricate hand embroidery and fine fabric.', 'https://miah.shop/_next/image?url=https%3A%2F%2Fimages.miah.shop%2Fproduct%2F%2Fm_thumb%2FStandard_Saree_Shewly_1001_3196A_1.jpg&w=1920&q=75'),
('Casual T-Shirt', 'T-Shirt', 600.00, 100, 'None', 'Comfortable casual t-shirt available in multiple colors.', 'https://4.imimg.com/data4/KS/HD/MY-718120/mens-casual-t-shirts.jpg'),
('Denim Jeans', 'Jeans', 2200.00, 45, 'None', 'Classic denim jeans with perfect fit and durability.', 'https://fabrilife.com/products/651830ea3218b-square.png?v=20'),
('Traditional Lehenga', 'Lehenga', 6500.00, 10, 'Hand Embroidered', 'Exquisite traditional lehenga with heavy embroidery work for weddings.', 'https://img0.junaroad.com/uiproducts/20970499/pri_175_p-1708088695.jpg'),
('Polo Shirt', 'Shirt', 1100.00, 60, 'None', 'Classic polo shirt for casual and semi-formal occasions.', 'https://xcdn.next.co.uk/common/items/default/default/itemimages/3_4Ratio/product/lge/K90240s.jpg?im=Resize,width=750'),
('Cotton Handloom Saree', 'Saree', 2800.00, 30, 'None', 'Pure cotton handloom saree with traditional border design.', 'https://img.drz.lazcdn.com/static/bd/p/1b868570bafaa1307410c1a89a8e4b10.jpg_200x200q80.avif'),
('Designer Georgette Saree', 'Saree', 3500.00, 20, 'Machine Embroidered', 'Lightweight georgette saree with modern embroidery patterns.', 'https://www.smarteshopbd.com/wp-content/uploads/2025/11/saree27.webp'),
('Banarasi Silk Saree', 'Saree', 6500.00, 15, 'Hand Embroidered', 'Premium Banarasi silk saree with intricate zari work.', 'https://www.karagiri.com/cdn/shop/products/banarasi-saree-mahogany-maroon-banarasi-saree-silk-saree-online-31828994130113_300x.jpg?v=1754985941'),
('Printed Chiffon Saree', 'Saree', 1800.00, 40, 'None', 'Trendy printed chiffon saree for casual and party wear.', 'https://peachmode.com/cdn/shop/files/1_JNX-RUCHI-STAR122-24904A.jpg?v=1695467424'),
('Kanjivaram Silk Saree', 'Saree', 7500.00, 12, 'Hand Embroidered', 'Authentic Kanjivaram silk saree with temple border.', 'https://rongpolli.com/storage/2024/09/Kanjivaram-Saree-1850-2.jpg'),
('Party Wear Saree', 'Saree', 3800.00, 22, 'Machine Embroidered', 'Glamorous party wear saree with sequin work.', 'https://cdn.sapnaaz.com/uploads/2024/10/15172505/1307-1-1.webp'),
('Jamdani Saree', 'Saree', 5200.00, 14, 'Hand Embroidered', 'Traditional Jamdani saree with fine muslin fabric.', 'https://tskbd.com/wp-content/uploads/2023/04/TSK-4.jpg'),
('Embroidered Net Saree', 'Saree', 3200.00, 25, 'Machine Embroidered', 'Elegant net saree with beautiful embroidery work.', 'https://medias.utsavfashion.com/media/catalog/product/cache/1/image/1000x/040ec09b1e35df139433887a97daa66f/e/m/embroidered-net-saree-in-off-white-v1-spta13205.jpg'),
('Designer Punjabi', 'Punjabi', 2800.00, 25, 'Machine Embroidered', 'Modern designer punjabi with contemporary patterns.', 'https://cdn.shopify.com/s/files/1/0549/6586/2483/files/high-quality-unique-boutique-designer-panjabi-9979131_360x.jpg?v=1760551816'),
('Casual Punjabi', 'Punjabi', 1500.00, 50, 'None', 'Simple casual punjabi for everyday comfort.', 'https://www.adlibbd.com/public/uploads/all/b6fff3664570345d98f682596b2fa3de-252141.jpg'),
('Anarkali Suit', 'Salwar Kameez', 3800.00, 18, 'Machine Embroidered', 'Elegant Anarkali suit with flowing silhouette.', 'https://citystanja.com/cdn/shop/files/1-14-269098-l-1-_1.jpg?v=1695453009&width=800'),
('Palazzo Set', 'Kurti', 1800.00, 30, 'None', 'Trendy kurti with palazzo pants combination.', 'https://adn-static1.nykaa.com/nykdesignstudio-images/pub/media/catalog/product/7/e/7e741abLP-AS71_1.jpg?tr=w-512'),
('Cotton Kurti', 'Kurti', 900.00, 50, 'None', 'Comfortable cotton kurti for daily wear.', 'https://www.aarong.com/_next/image?url=https%3A%2F%2Fmcprod.aarong.com%2Fmedia%2Fcatalog%2Fproduct%2F1%2F1%2F1190000014549.jpg%3Foptimize%3Dhigh%26bg-color%3D255%2C255%2C255%26fit%3Dbounds%26height%3D%26width%3D&w=640&q=75'),
('Sharara Set', 'Salwar Kameez', 4200.00, 14, 'Hand Embroidered', 'Traditional sharara set with rich embroidery.', 'https://narayanivastra.in/cdn/shop/files/NV_0295_1.jpg?v=1736109444&width=1946'),
('Chino Pants', 'Pants', 1800.00, 40, 'None', 'Stylish chino pants for smart casual look.', 'https://fabrilife.com/products/657bef5d855de-square.jpg?v=20'),
('Hoodie', 'Jacket', 2000.00, 35, 'None', 'Cozy hoodie for winter and casual outings.', 'https://bdmanja.com/wp-content/uploads/2020/11/20250925_1429_Gray-Hoodie-Design_remix_01k5zzr4z4ff190hdbksxt8pg7-300x300.jpg'),
('Cargo Pants', 'Pants', 1900.00, 30, 'None', 'Functional cargo pants with multiple pockets.', 'https://fabrilife.com/products/66c1f1a62c62b-square.jpg?v=20'),
('Track Pants', 'Pants', 1300.00, 55, 'None', 'Comfortable track pants for sports and leisure.', 'https://assets.adidas.com/images/w_600,f_auto,q_auto/c87749bc2db8494c94a4c14aa3718d38_faec/Adicolor_Baggy_Fit_Firebird_Track_Pants_Black_IZ4801_db21_model.tiff.jpg'),
('Denim Jacket', 'Jacket', 2800.00, 25, 'None', 'Classic denim jacket for all seasons.', 'https://images.wrangler.com/is/image/Wrangler/RJK30AN-HERO?$KDP-XXLARGE$'),
('Pashmina Shawl', 'Accessories', 2500.00, 20, 'Hand Embroidered', 'Luxurious pashmina shawl with delicate embroidery.', 'https://www.pashtush.com/cdn/shop/files/pashtush-pashmina-pashtush-women-faux-pashmina-shawl-ethnic-weave-design-black-30746399899702.jpg?v=1712866883&width=1080'),
('Embroidered Stole', 'Accessories', 1200.00, 30, 'Machine Embroidered', 'Stylish embroidered stole for ethnic wear.', 'https://www.weaversvilla.com/cdn/shop/products/81EDtXpKnHL._UL1500.jpg?v=1600007348'),
('Designer Belt', 'Accessories', 600.00, 50, 'None', 'Premium leather belt with designer buckle.', 'https://www.flannels.com/images/products/94521303_h_a1.jpg'),
('Embroidered Handbag', 'Accessories', 1800.00, 18, 'Hand Embroidered', 'Handcrafted embroidered handbag.', 'https://www.fableengland.com/cdn/shop/files/6c7ab8fe-0260-47d6-9e16-35fcbcfe6a79.jpg?v=1751284278&width=1080'),
('Silk Scarf', 'Accessories', 700.00, 45, 'None', 'Smooth silk scarf in vibrant colors.', 'https://img.drz.lazcdn.com/static/bd/p/3803893e549799c8eb2d5e6730193abc.jpg_720x720q80.jpg'),
('Clutch Bag', 'Accessories', 1000.00, 28, 'Machine Embroidered', 'Elegant clutch bag for parties and events.', 'https://img.drz.lazcdn.com/static/bd/p/78abc22aaa3d62424055b154562d9552.jpg_200x200q80.avif'),
('Embroidered Cap', 'Accessories', 500.00, 60, 'Machine Embroidered', 'Traditional embroidered cap for men.', 'https://www.custompatchhats.com/wp-content/uploads/2022/07/Direct-Embroidery-Mountain-outdoorsy-hats.jpg');

-- Sample Reviews
INSERT INTO Review (CustomerID, ProductID, Rating, Comment) VALUES
(1, 1, 5, 'Excellent quality saree! The embroidery work is amazing.'),
(2, 2, 4, 'Good product. Comfortable to wear.'),
(1, 5, 5, 'Absolutely beautiful! Worth every penny.');

-- Sample Ranking
INSERT INTO Ranking (CustomerID, ProductID, Quantity) VALUES
(1, 1, 5),
(1, 5, 5),
(2, 2, 4);
