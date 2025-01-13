/**
 * Artillery Test Functions
 * Version: 1.0.0
 * Last Updated: 2025-01-10
 */

const faker = require('faker');

function generateUser(requestParams, context, ee, next) {
  context.vars.email = faker.internet.email();
  context.vars.password = 'testpass123';
  context.vars.firstName = faker.name.firstName();
  context.vars.lastName = faker.name.lastName();
  return next();
}

function generateTenant(requestParams, context, ee, next) {
  const name = faker.company.companyName();
  context.vars.tenantName = name;
  context.vars.tenantSlug = name.toLowerCase().replace(/[^a-z0-9]/g, '-');
  return next();
}

function generateInventoryItem(requestParams, context, ee, next) {
  context.vars.itemName = faker.commerce.productName();
  context.vars.itemDescription = faker.commerce.productDescription();
  context.vars.itemQuantity = faker.datatype.number({ min: 1, max: 100 });
  context.vars.itemPrice = parseFloat(faker.commerce.price());
  return next();
}

function generateOrder(requestParams, context, ee, next) {
  context.vars.customerName = faker.name.findName();
  context.vars.customerEmail = faker.internet.email();
  context.vars.address = faker.address.streetAddress();
  context.vars.orderQuantity = faker.datatype.number({ min: 1, max: 5 });
  context.vars.discount = faker.datatype.number({ min: 0, max: 20 });
  return next();
}

function setAuthHeader(requestParams, context, ee, next) {
  requestParams.headers = {
    ...requestParams.headers,
    'Authorization': `Bearer ${context.vars.token}`
  };
  return next();
}

module.exports = {
  generateUser,
  generateTenant,
  generateInventoryItem,
  generateOrder,
  setAuthHeader
};
