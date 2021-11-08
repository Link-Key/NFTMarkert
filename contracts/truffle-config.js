
require('dotenv').config();
const BN = require('bn.js');
const { TEST_MNEMONIC } = require('./test/helpers/constants.js');
const HDWalletProvider = require("@truffle/hdwallet-provider");

module.exports = {
    networks: {
        mainnet: {
            provider: function() {
                return new HDWalletProvider({
                    mnemonic: {
                        phrase: process.env.MNEMONIC
                    },
                    providerOrUrl: `https://mainnet.infura.io/v3/${process.env.INFURA_API_KEY}`,
                    addressIndex: 0,
                    numberOfAddresses: 10
                })
            },
            // gas: 5000000,
            gasPrice: parseInt((new BN(125).mul(new BN(10).pow(new BN(9)))).toString()),
            confirmations: 2,
            network_id: 1
        },
        ropsten: {
            provider: function() {
                // return new HDWalletProvider(TEST_MNEMONIC, 'http://127.0.0.1:7545')
                // return new HDWalletProvider(TEST_MNEMONIC, `https://ropsten.infura.io/v3/${process.env.INFURA_API_KEY}`)
                // return new HDWalletProvider(TEST_MNEMONIC, `https://kovan.infura.io/v3/${process.env.INFURA_API_KEY}`)

                return new HDWalletProvider({
                    mnemonic: {
                        phrase: 'apple security pepper comic jazz gown pluck curve door once popular muscle'
                    },
                    providerOrUrl: `https://ropsten.infura.io/v3/${process.env.INFURA_API_KEY}`,
                    addressIndex: 0,
                    numberOfAddresses: 10
                })
            },
            // gas: 8000000,
            gasPrice: parseInt((new BN(145).mul(new BN(10).pow(new BN(9)))).toString()),
            network_id: 3
        },
        dev: {
            provider: function() {
                return new HDWalletProvider('brand flower still purity devote struggle cradle later defense ginger beef safe', 'http://127.0.0.1:7545')
            },
            // gas: 8000000,
            gasPrice: parseInt((new BN(100).mul(new BN(10).pow(new BN(9)))).toString()),
            network_id: 5777
        },
        development: {
            provider: function() {
                return new HDWalletProvider(TEST_MNEMONIC, "http://127.0.0.1:7545")
            },
            //gas: 5000000,
            gasPrice: parseInt((new BN(145).mul(new BN(10).pow(new BN(9)))).toString()),
            network_id: 5777
        }
    },
    // Configure your compilers
    compilers: {
        solc: {
            version: "^0.7.6",    // Fetch exact version from solc-bin (default: truffle's version)
            // docker: true ,
            settings: {          // See the solidity docs for advice about optimization and evmVersion
                optimizer: {
                    enabled: false,
                    runs: 200
                }
                //  evmVersion: "byzantium"
            }
        }
    },
    plugins: ["solidity-coverage"]
}