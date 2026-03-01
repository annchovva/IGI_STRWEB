const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  entry: './index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js'
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: { presets: ['@babel/preset-react'] }
        }
      }
    ]
  },
  plugins: [ new HtmlWebpackPlugin({ template: './index.html' }) ],
  devServer: {
    host: '0.0.0.0',
    port: 3000,
    historyApiFallback: true
  }
};
