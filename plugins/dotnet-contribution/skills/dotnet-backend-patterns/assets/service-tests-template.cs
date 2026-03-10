// Service Tests Template for .NET 8+
using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using FluentValidation;
using Moq;
using Xunit;
using YourNamespace.Application.Services;

namespace YourNamespace.Application.Tests.Services;

public class ProductServiceTests
{
    private readonly Mock<IProductRepository> _mockRepository;
    private readonly Mock<ICacheService> _mockCache;
    private readonly Mock<IValidator<CreateProductRequest>> _mockCreateValidator;
    private readonly Mock<IValidator<UpdateProductRequest>> _mockUpdateValidator;
    private readonly Mock<ILogger<ProductService>> _mockLogger;
    private readonly ProductServiceOptions _options;
    private readonly ProductService _sut;

    public ProductServiceTests()
    {
        _mockRepository = new Mock<IProductRepository>();
        _mockCache = new Mock<ICacheService>();
        _mockCreateValidator = new Mock<IValidator<CreateProductRequest>>();
        _mockUpdateValidator = new Mock<IValidator<UpdateProductRequest>>();
        _mockLogger = new Mock<ILogger<ProductService>>();

        _options = new ProductServiceOptions { CacheDuration = TimeSpan.FromMinutes(15) };
        var mockOptions = Options.Create(_options);

        _sut = new ProductService(
            _mockRepository.Object,
            _mockCache.Object,
            _mockCreateValidator.Object,
            _mockUpdateValidator.Object,
            _mockLogger.Object,
            mockOptions);
    }

    [Fact]
    public async Task GetByIdAsync_WhenProductInCache_ReturnsCachedProduct()
    {
        // Arrange
        var id = "prod-1";
        var cacheKey = $"product:{id}";
        var cachedProduct = new Product { Id = id, Name = "Cached Product" };

        _mockCache
            .Setup(c => c.GetAsync<Product>(cacheKey, It.IsAny<CancellationToken>()))
            .ReturnsAsync(cachedProduct);

        // Act
        var result = await _sut.GetByIdAsync(id);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.Equal("Cached Product", result.Value?.Name);
        _mockRepository.Verify(r => r.GetByIdAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()), Times.Never);
    }

    [Fact]
    public async Task GetByIdAsync_WhenProductNotInCache_FetchesFromRepositoryAndCaches()
    {
        // Arrange
        var id = "prod-1";
        var cacheKey = $"product:{id}";
        var dbProduct = new Product { Id = id, Name = "DB Product" };

        _mockCache
            .Setup(c => c.GetAsync<Product>(cacheKey, It.IsAny<CancellationToken>()))
            .ReturnsAsync((Product?)null);

        _mockRepository
            .Setup(r => r.GetByIdAsync(id, It.IsAny<CancellationToken>()))
            .ReturnsAsync(dbProduct);

        // Act
        var result = await _sut.GetByIdAsync(id);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.Equal("DB Product", result.Value?.Name);

        _mockRepository.Verify(r => r.GetByIdAsync(id, It.IsAny<CancellationToken>()), Times.Once);
        _mockCache.Verify(c => c.SetAsync(cacheKey, dbProduct, _options.CacheDuration, It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task GetByIdAsync_WhenProductNotFoundInRepository_ReturnsFailureAndDoesNotCache()
    {
        // Arrange
        var id = "prod-1";
        var cacheKey = $"product:{id}";

        _mockCache
            .Setup(c => c.GetAsync<Product>(cacheKey, It.IsAny<CancellationToken>()))
            .ReturnsAsync((Product?)null);

        _mockRepository
            .Setup(r => r.GetByIdAsync(id, It.IsAny<CancellationToken>()))
            .ReturnsAsync((Product?)null);

        // Act
        var result = await _sut.GetByIdAsync(id);

        // Assert
        Assert.False(result.IsSuccess);
        Assert.Equal("NOT_FOUND", result.ErrorCode);

        _mockCache.Verify(c => c.SetAsync(It.IsAny<string>(), It.IsAny<Product>(), It.IsAny<TimeSpan>(), It.IsAny<CancellationToken>()), Times.Never);
    }
}

// Required interfaces not defined in the original templates
namespace YourNamespace.Application.Services
{
    public interface ICacheService
    {
        Task<T?> GetAsync<T>(string key, CancellationToken ct = default);
        Task SetAsync<T>(string key, T value, TimeSpan? expiration = null, CancellationToken ct = default);
        Task RemoveAsync(string key, CancellationToken ct = default);
    }
}
