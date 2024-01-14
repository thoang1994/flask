provider "aws" {
  region = "ap-southeast-1"  // Thay thế bằng khu vực AWS của bạn
}

resource "aws_vpc" "my_vpc" {
  cidr_block = "10.0.0.0/16"  # Specify the CIDR block for your VPC

  tags = {
    Name = "thoang1"
  }
}

# Tạo Internet Gateway
resource "aws_internet_gateway" "my_igw" {
  vpc_id = aws_vpc.my_vpc.id

  tags = {
    Name = "MyIGW"
  }
}

# Tạo Route Table cho public subnet
resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.my_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.my_igw.id
  }

  tags = {
    Name = "PublicRouteTable"
  }
}

# Tạo public subnet và associate với public route table
resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.my_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "ap-southeast-1a"   # Chọn khu vực mong muốn
  map_public_ip_on_launch = true

  tags = {
    Name = "PublicSubnet"
  }
}

# Associate public subnet with public route table
resource "aws_route_table_association" "public_subnet_association" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_route_table.id
}

# Tạo private subnet và associate với default route table (private subnet không có đường đi ra Internet)
resource "aws_subnet" "private_subnet" {
  vpc_id                  = aws_vpc.my_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "ap-southeast-1a"  # Chọn khu vực mong muốn
  map_public_ip_on_launch = false

  tags = {
    Name = "PrivateSubnet"
  }
}

# Tạo security group cho public subnet
# Tạo security group cho public subnet
resource "aws_security_group" "public_sg" {
  vpc_id = aws_vpc.my_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # Thêm các quy tắc khác nếu cần thiết

  tags = {
    Name = "PublicSG"
  }
}


# Tạo security group cho private subnet
resource "aws_security_group" "private_sg" {
  vpc_id = aws_vpc.my_vpc.id

  # Thêm các quy tắc cần thiết cho private subnet

  tags = {
    Name = "PrivateSG"
  }
}


# Tạo EC2 instance trong public subnet
resource "aws_instance" "my_ec2_instance" {
  ami           = "ami-03caf91bb3d81b843"  # Replace with your desired AMI ID
  instance_type = "t2.micro"
  key_name      = "thoang3"  # Replace with your key pair name
  subnet_id     = aws_subnet.public_subnet.id

  security_groups = [aws_security_group.public_sg.id]  # Link to the public security group

  user_data = <<-EOF
              #!/bin/bash
              apt update
              apt install -y docker-compose
              apt install -y git
              git clone https://github.com/thoang1994/flask.git
              cd $PWD flask
              docker-compose up -d
              EOF

  tags = {
    Name = "MyEC2Instance"
  }
}


