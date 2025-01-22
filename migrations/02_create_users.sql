-- Create a user for the 'estoque' database
CREATE USER 'frame_extractor_user'@'%' IDENTIFIED BY 'Mudar123!';
GRANT ALL PRIVILEGES ON frame_extractor.* TO 'frame_extractor_user'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;
