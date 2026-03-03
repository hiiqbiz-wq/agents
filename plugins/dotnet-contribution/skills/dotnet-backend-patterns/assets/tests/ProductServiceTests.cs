using System;
using System.Threading;
using System.Threading.Tasks;
using FluentValidation;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Moq;
using Xunit;
using YourNamespace.Application.Services;

namespace YourNamespace.Application.Tests
{
    public class ProductServiceTests
    {
        private readonly Mock<IProductRepository> _mockRepository;
        private readonly Mock<ICacheService> _mockCache;
        private readonly Mock<IValidator<CreateProductRequest>> _mockCreateValidator;
        private readonly Mock<IValidator<UpdateProductRequest>> _mockUpdateValidator;
        private readonly Mock<ILogger<ProductService>> _mockLogger;
        private readonly Mock<IOptions<ProductServiceOptions>> _mockOptions;

        private readonly ProductService _sut;

        public ProductServiceTests()
        {
            _mockRepository = new Mock<IProductRepository>();
            _mockCache = new Mock<ICacheService>();
            _mockCreateValidator = new Mock<IValidator<CreateProductRequest>>();
            _mockUpdateValidator = new Mock<IValidator<UpdateProductRequest>>();
            _mockLogger = new Mock<ILogger<ProductService>>();
            _mockOptions = new Mock<IOptions<ProductServiceOptions>>();

            _mockOptions.Setup(o => o.Value).Returns(new ProductServiceOptions { CacheDuration = TimeSpan.FromMinutes(15) });

            _sut = new ProductService(
                _mockRepository.Object,
                _mockCache.Object,
                _mockCreateValidator.Object,
                _mockUpdateValidator.Object,
                _mockLogger.Object,
                _mockOptions.Object);
        }

        [Fact]
        public async Task GetByIdAsync_WhenFoundInCache_ReturnsCachedProduct()
        {
            // Arrange
            var id = "prod-1";
            var cachedProduct = new Product { Id = id, Name = "Cached Product" };

            _mockCache.Setup(c => c.GetAsync<Product>($"product:{id}", It.IsAny<CancellationToken>()))
                      .ReturnsAsync(cachedProduct);

            // Act
            var result = await _sut.GetByIdAsync(id);

            // Assert
            Assert.True(result.IsSuccess);
            Assert.Equal(cachedProduct, result.Value);

            _mockRepository.Verify(r => r.GetByIdAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()), Times.Never);
        }

        [Fact]
        public async Task GetByIdAsync_WhenNotInCacheButInRepo_FetchesFromRepoAndCaches()
        {
            // Arrange
            var id = "prod-2";
            var repoProduct = new Product { Id = id, Name = "Repo Product" };

            _mockCache.Setup(c => c.GetAsync<Product>($"product:{id}", It.IsAny<CancellationToken>()))
                      .ReturnsAsync((Product)null);

            _mockRepository.Setup(r => r.GetByIdAsync(id, It.IsAny<CancellationToken>()))
                           .ReturnsAsync(repoProduct);

            // Act
            var result = await _sut.GetByIdAsync(id);

            // Assert
            Assert.True(result.IsSuccess);
            Assert.Equal(repoProduct, result.Value);

            _mockCache.Verify(c => c.SetAsync($"product:{id}", repoProduct, TimeSpan.FromMinutes(15), It.IsAny<CancellationToken>()), Times.Once);
        }

        [Fact]
        public async Task GetByIdAsync_WhenEmptyId_ReturnsFailure()
        {
            // Act
            var result = await _sut.GetByIdAsync(string.Empty);

            // Assert
            Assert.False(result.IsSuccess);
            Assert.Equal("INVALID_ID", result.ErrorCode);
        }

        [Fact]
        public async Task GetByIdAsync_WhenExceptionThrown_ReturnsInternalErrorFailure()
        {
            // Arrange
            var id = "prod-3";
            _mockCache.Setup(c => c.GetAsync<Product>(It.IsAny<string>(), It.IsAny<CancellationToken>()))
                      .ThrowsAsync(new Exception("Cache failure"));

            // Act
            var result = await _sut.GetByIdAsync(id);

            // Assert
            Assert.False(result.IsSuccess);
            Assert.Equal("INTERNAL_ERROR", result.ErrorCode);
        }
    }
}
