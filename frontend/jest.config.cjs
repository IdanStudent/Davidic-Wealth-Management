module.exports = {
  testEnvironment: 'jest-environment-jsdom',
  transform: {
    '^.+\\.jsx?$': 'babel-jest'
  },
  moduleNameMapper: {
    '\\.(css|less|scss)$': 'identity-obj-proxy',
    '^react-chartjs-2$': '<rootDir>/src/test/__mocks__/react-chartjs-2.js'
  },
  setupFilesAfterEnv: ["@testing-library/jest-dom/extend-expect"]
}
