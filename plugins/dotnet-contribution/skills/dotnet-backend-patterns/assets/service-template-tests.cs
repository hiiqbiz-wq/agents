using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using FluentValidation;
using FluentValidation.Results;
using Xunit;
using YourNamespace.Application.Services;

namespace YourNamespace.Application.Services.Tests;

public class CreateProductRequestValidatorTests
{
    private readonly CreateProductRequestValidator _validator;

    public CreateProductRequestValidatorTests()
    {
        _validator = new CreateProductRequestValidator();
    }

    [Fact]
    public void Validate_ValidRequest_ShouldNotHaveAnyErrors()
    {
        // Arrange
        var request = new CreateProductRequest("Valid Product Name", "SKU-12345", 99.99m, 1);

        // Act
        var result = _validator.Validate(request);

        // Assert
        Assert.True(result.IsValid);
    }

    [Theory]
    [InlineData("")]
    [InlineData(" ")]
    [InlineData(null)]
    public void Validate_EmptyName_ShouldHaveValidationError(string? invalidName)
    {
        // Arrange
        var request = new CreateProductRequest(invalidName ?? string.Empty, "SKU-12345", 99.99m, 1);

        // Act
        var result = _validator.Validate(request);

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, e => e.PropertyName == "Name" && e.ErrorMessage == "Name is required");
    }

    [Fact]
    public void Validate_NameExceedsMaxLength_ShouldHaveValidationError()
    {
        // Arrange
        var request = new CreateProductRequest(new string('A', 201), "SKU-12345", 99.99m, 1);

        // Act
        var result = _validator.Validate(request);

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, e => e.PropertyName == "Name" && e.ErrorMessage == "Name must not exceed 200 characters");
    }

    [Theory]
    [InlineData("")]
    [InlineData(" ")]
    [InlineData(null)]
    public void Validate_EmptySku_ShouldHaveValidationError(string? invalidSku)
    {
        // Arrange
        var request = new CreateProductRequest("Valid Product Name", invalidSku ?? string.Empty, 99.99m, 1);

        // Act
        var result = _validator.Validate(request);

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, e => e.PropertyName == "Sku" && e.ErrorMessage == "SKU is required");
    }

    [Fact]
    public void Validate_SkuExceedsMaxLength_ShouldHaveValidationError()
    {
        // Arrange
        var request = new CreateProductRequest("Valid Product Name", new string('A', 51), 99.99m, 1);

        // Act
        var result = _validator.Validate(request);

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, e => e.PropertyName == "Sku" && e.ErrorMessage == "SKU must not exceed 50 characters");
    }

    [Theory]
    [InlineData("invalid_sku")]
    [InlineData("SKU 123")]
    [InlineData("sku-123")]
    [InlineData("SKU@123")]
    public void Validate_InvalidSkuFormat_ShouldHaveValidationError(string invalidSku)
    {
        // Arrange
        var request = new CreateProductRequest("Valid Product Name", invalidSku, 99.99m, 1);

        // Act
        var result = _validator.Validate(request);

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, e => e.PropertyName == "Sku" && e.ErrorMessage == "SKU must contain only uppercase letters, numbers, and hyphens");
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-10.5)]
    public void Validate_InvalidPrice_ShouldHaveValidationError(decimal invalidPrice)
    {
        // Arrange
        var request = new CreateProductRequest("Valid Product Name", "SKU-123", invalidPrice, 1);

        // Act
        var result = _validator.Validate(request);

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, e => e.PropertyName == "Price" && e.ErrorMessage == "Price must be greater than 0");
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-1)]
    public void Validate_InvalidCategoryId_ShouldHaveValidationError(int invalidCategoryId)
    {
        // Arrange
        var request = new CreateProductRequest("Valid Product Name", "SKU-123", 99.99m, invalidCategoryId);

        // Act
        var result = _validator.Validate(request);

        // Assert
        Assert.False(result.IsValid);
        Assert.Contains(result.Errors, e => e.PropertyName == "CategoryId" && e.ErrorMessage == "Category is required");
    }
}
