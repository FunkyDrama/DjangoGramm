const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const {WebpackManifestPlugin} = require('webpack-manifest-plugin');

module.exports = (env, argv) => {
    const isProduction = argv.mode === 'production';

    return {
        entry: './src/index.js',

        output: {
            path: path.resolve(__dirname, '../static/dist'),
            filename: isProduction ? 'bundle.[contenthash].js' : 'bundle.js',
            clean: true,
            publicPath: '/static/dist/',
        },

        module: {
            rules: [
                {
                    test: /\.css$/,
                    use: [
                        MiniCssExtractPlugin.loader,
                        'css-loader',
                        'postcss-loader',
                    ],
                },
                {
                    test: /\.(svg|png|jpg|jpeg|gif)$/i,
                    type: 'asset/resource',
                    generator: {
                        filename: 'images/[name][ext]'
                    },
                    sideEffects: true,
                }
            ],
        },

        plugins: [
            new MiniCssExtractPlugin({
                filename: isProduction ? 'bundle.[contenthash].css' : 'bundle.css',
            }),
            new WebpackManifestPlugin({
                fileName: 'manifest.json',
                publicPath: '',
                generate: (seed, files, entrypoints) => {
                    const manifestFiles = files.reduce((manifest, file) => {
                        manifest[file.name] = file.path;
                        return manifest;
                    }, seed);

                    const entryFiles = entrypoints.main || [];
                    entryFiles.forEach(fileName => {
                        if (fileName.endsWith('.js')) {
                            manifestFiles['bundle.js'] = fileName;
                        }
                        if (fileName.endsWith('.css')) {
                            manifestFiles['bundle.css'] = fileName;
                        }
                    });

                    return manifestFiles;
                },
            }),
        ],

        mode: argv.mode || 'development',
        devtool: isProduction ? 'source-map' : 'eval-source-map',
    };
};